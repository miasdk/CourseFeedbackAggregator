"""
Canvas Quiz Reports API Client

Handles quiz report generation, polling, and CSV data extraction.
This is the PRIMARY method for extracting complete student quiz responses from Canvas,
including essay/text responses that are not available via other APIs.

Official Canvas API Endpoints:
- POST /api/v1/courses/:course_id/quizzes/:quiz_id/reports (generate report)
- GET /api/v1/courses/:course_id/quizzes/:quiz_id/reports/:id (check status)
- GET <file_url> (download CSV)

Documentation:
- Quiz Reports: https://canvas.instructure.com/doc/api/quiz_reports.html
"""

from typing import Dict, List, Any
import asyncio
from datetime import datetime
import pandas as pd
from io import StringIO
import httpx
from .base import CanvasBaseClient


class CanvasQuizReportsClient(CanvasBaseClient):
    """
    Client for Canvas Quiz Reports API.

    Provides complete workflow for extracting student quiz responses:
    1. Generate student_analysis report
    2. Poll for completion
    3. Download CSV file
    4. Parse and structure data

    Example usage:
        client = CanvasQuizReportsClient()
        responses = await client.get_all_student_responses(course_id=42, quiz_id=481)
    """

    async def generate_report(
        self,
        course_id: int,
        quiz_id: int,
        report_type: str = "student_analysis"
    ) -> Dict[str, Any]:
        """
        Generate a quiz report.

        Official API: POST /api/v1/courses/:course_id/quizzes/:quiz_id/reports

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID
            report_type: Type of report (default: "student_analysis")

        Returns:
            Report generation response with report_id

        Report Types:
            - student_analysis: Individual student responses (RECOMMENDED for feedback)
            - item_analysis: Question-level statistics
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports"

        payload = {
            "quiz_report[report_type]": report_type,
            "quiz_report[includes_all_versions]": "true"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                data=payload
            )
            response.raise_for_status()
            return response.json()

    async def get_report_status(
        self,
        course_id: int,
        quiz_id: int,
        report_id: int
    ) -> Dict[str, Any]:
        """
        Get report generation status.

        Official API: GET /api/v1/courses/:course_id/quizzes/:quiz_id/reports/:id

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID
            report_id: Report ID from generate_report()

        Returns:
            Report status dict with optional file URL
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports/{report_id}"
        return await self._get_single(endpoint)

    async def poll_report_completion(
        self,
        course_id: int,
        quiz_id: int,
        report_id: int,
        max_wait_seconds: int = 300,
        poll_interval: float = 2.0
    ) -> str:
        """
        Poll report status until CSV file is ready for download.

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID
            report_id: Report ID from generate_report()
            max_wait_seconds: Maximum time to wait (default: 300s / 5 minutes)
            poll_interval: Seconds between status checks (default: 2.0)

        Returns:
            CSV file download URL

        Raises:
            TimeoutError: If report generation exceeds max_wait_seconds
            Exception: If report generation fails
        """
        start_time = datetime.now()

        while True:
            status = await self.get_report_status(course_id, quiz_id, report_id)

            # Check if CSV file is ready
            if status.get('file') and status['file'].get('url'):
                return status['file']['url']

            # Check for error state
            workflow_state = status.get('workflow_state')
            if workflow_state == 'error':
                raise Exception(f"Report generation failed for report {report_id}")

            # Timeout protection
            elapsed = (datetime.now() - start_time).seconds
            if elapsed > max_wait_seconds:
                raise TimeoutError(
                    f"Report generation exceeded {max_wait_seconds}s timeout"
                )

            await asyncio.sleep(poll_interval)

    async def download_csv(self, file_url: str) -> pd.DataFrame:
        """
        Download and parse quiz report CSV.

        Args:
            file_url: CSV download URL from poll_report_completion()

        Returns:
            pandas DataFrame with student responses

        CSV Structure:
            name,id,section,section_id,3627: How Effective...,3628: What was...
            Emily Voytecek,21089,Default,123,Excellent,"The case study module..."
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(file_url)
            response.raise_for_status()

            # Parse CSV content
            csv_content = StringIO(response.text)
            df = pd.read_csv(csv_content)

            return df

    async def get_all_student_responses(
        self,
        course_id: int,
        quiz_id: int
    ) -> List[Dict[str, Any]]:
        """
        Complete workflow: Generate report, poll completion, download and parse CSV.

        This is the main method to extract ALL student quiz responses including essay text.

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID

        Returns:
            List of student response dictionaries

        Example return:
            [
                {
                    "student_canvas_id": 21089,
                    "student_name": "Emily Voytecek",
                    "responses": [
                        {
                            "question_id": 3627,
                            "question_text": "How Effective was the OVERALL Program?",
                            "answer": "Excellent"
                        },
                        {
                            "question_id": 3628,
                            "question_text": "What was your favorite part...",
                            "answer": "The case study module. The speaker's anecdotes..."
                        }
                    ]
                }
            ]
        """
        # Step 1: Generate report
        print(f"Generating student_analysis report for quiz {quiz_id}...")
        report = await self.generate_report(course_id, quiz_id)
        report_id = report['id']
        print(f"  Report ID: {report_id}")

        # Step 2: Poll until ready
        print(f"Polling report {report_id} for completion...")
        csv_url = await self.poll_report_completion(course_id, quiz_id, report_id)
        print(f"  CSV ready!")

        # Step 3: Download CSV
        print(f"Downloading CSV...")
        df = await self.download_csv(csv_url)
        print(f"  Downloaded {len(df)} student responses")

        # Step 4: Structure data
        return self._structure_responses(df)

    def _structure_responses(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Transform CSV DataFrame into structured response data.

        CSV Column Format:
            - name: Student name
            - id: Student Canvas ID
            - section: Section name
            - section_id: Section ID
            - <question_id>: <question_text>: Answer columns (one per question)

        Args:
            df: pandas DataFrame from CSV

        Returns:
            List of structured student response dicts
        """
        structured_responses = []

        # Extract question columns (format: "3627: How Effective...")
        # Exclude metadata columns
        metadata_cols = ['name', 'id', 'section', 'section_id', 'section_sis_id',
                        'sis_id', 'submitted', 'attempt']
        question_columns = [col for col in df.columns
                           if ':' in col and col not in metadata_cols]

        for _, row in df.iterrows():
            # Student metadata
            student_id = row.get('id')
            student_name = row.get('name')

            # Extract question responses
            responses = []
            for col in question_columns:
                # Parse question ID and text from column name
                # Format: "3627: How would you rate..."
                parts = col.split(':', 1)
                if len(parts) < 2:
                    continue

                question_id = int(parts[0].strip())
                question_text = parts[1].strip()

                # Get answer value
                answer = row.get(col)

                # Skip if answer is NaN/empty
                if pd.isna(answer):
                    continue

                responses.append({
                    "question_id": question_id,
                    "question_text": question_text,
                    "answer": str(answer)
                })

            # Only add if student has at least one response
            if responses:
                structured_responses.append({
                    "student_canvas_id": int(student_id) if pd.notna(student_id) else None,
                    "student_name": str(student_name) if pd.notna(student_name) else None,
                    "responses": responses
                })

        return structured_responses
