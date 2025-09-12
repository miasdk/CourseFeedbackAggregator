"""Course name normalization utilities for Canvas and Zoho data."""

import re
from typing import Dict, Optional, Tuple


class CourseNormalizer:
    """Normalize course names from different sources to consistent format."""
    
    # Common university abbreviations and full names
    INSTITUTION_MAPPINGS = {
        'HCU': 'Houston Christian University',
        'ACU': 'Arizona Christian University',
        'AU': 'Ashland University',
        'TCU': 'Texas Christian University',
        'NYU': 'New York University',
        'UCLA': 'University of California Los Angeles',
        'MIT': 'Massachusetts Institute of Technology',
        'Stanford': 'Stanford University',
        'Harvard': 'Harvard University',
        'Yale': 'Yale University',
        'Princeton': 'Princeton University',
        'Columbia': 'Columbia University',
        'UPenn': 'University of Pennsylvania',
        'Northwestern': 'Northwestern University',
        'Duke': 'Duke University',
        'Rice': 'Rice University',
        'SMU': 'Southern Methodist University',
        'TCU': 'Texas Christian University',
        'Baylor': 'Baylor University',
        'UT': 'University of Texas',
        'TAMU': 'Texas A&M University',
    }
    
    # Program type patterns to identify and standardize
    PROGRAM_PATTERNS = {
        'Strategic AI': 'Strategic Artificial Intelligence Program',
        'AI Program': 'Strategic Artificial Intelligence Program',
        'Women in Leadership': 'Women in Leadership Program',
        'WIL': 'Women in Leadership Program',
        'Executive Education': 'Executive Education',
        'Exec Ed': 'Executive Education',
        'Professional Development': 'Professional Development',
        'Certificate Program': 'Certificate Program',
        'Leadership Development': 'Leadership Development Program',
        'Digital Transformation': 'Digital Transformation Program',
        'Innovation Management': 'Innovation Management Program',
    }
    
    # Course code patterns (e.g., ENROLL/AI-HCU/2023)
    ENROLLMENT_CODE_PATTERN = r'(ENROLL|Enroll|ENROLLMENT)/?([A-Z]+)-?([A-Z]+)/(\d{4})'
    
    @classmethod
    def extract_institution_from_name(cls, course_name: str) -> Tuple[Optional[str], str]:
        """
        Extract institution name from course name.
        Returns (institution, remaining_name)
        """
        if not course_name:
            return None, course_name
            
        # Check for explicit institution patterns
        for abbr, full_name in cls.INSTITUTION_MAPPINGS.items():
            # Check for abbreviation in various formats
            patterns = [
                rf'\b{abbr}\b',  # Word boundary match
                rf'^{abbr}\s*[-:]',  # At start with separator
                rf'[-:]\s*{abbr}$',  # At end with separator
                rf'\({abbr}\)',  # In parentheses
            ]
            
            for pattern in patterns:
                if re.search(pattern, course_name, re.IGNORECASE):
                    # Remove the abbreviation from the name
                    remaining = re.sub(pattern, '', course_name, flags=re.IGNORECASE).strip()
                    remaining = re.sub(r'^[-:]\s*', '', remaining).strip()  # Clean up separators
                    return full_name, remaining
                    
            # Also check for full institution name
            if full_name.lower() in course_name.lower():
                remaining = course_name.replace(full_name, '').replace(full_name.lower(), '').strip()
                remaining = re.sub(r'^[-:]\s*', '', remaining).strip()
                return full_name, remaining
        
        # Check for generic university patterns
        university_match = re.search(r'([\w\s]+)\s+(University|College|Institute|School)', course_name, re.IGNORECASE)
        if university_match:
            institution = university_match.group(0)
            remaining = course_name.replace(institution, '').strip()
            remaining = re.sub(r'^[-:]\s*', '', remaining).strip()
            return institution, remaining
            
        return None, course_name
    
    @classmethod
    def extract_program_type(cls, course_name: str) -> Tuple[Optional[str], str]:
        """
        Extract and standardize program type from course name.
        Returns (program_type, remaining_name)
        """
        # Check for known program patterns
        for pattern, standardized in cls.PROGRAM_PATTERNS.items():
            if pattern.lower() in course_name.lower():
                # Extract the program type and return standardized version
                remaining = re.sub(re.escape(pattern), '', course_name, flags=re.IGNORECASE).strip()
                return standardized, remaining
        
        # Check for generic program indicators
        program_match = re.search(r'(Certificate|Program|Course|Training|Workshop|Seminar)', course_name, re.IGNORECASE)
        if program_match:
            # Extract context around the program type
            full_match = re.search(rf'[\w\s]*{program_match.group(0)}', course_name, re.IGNORECASE)
            if full_match:
                return full_match.group(0), course_name.replace(full_match.group(0), '').strip()
                
        return None, course_name
    
    @classmethod
    def extract_enrollment_code(cls, course_name: str) -> Tuple[Optional[str], str]:
        """
        Extract enrollment code from course name.
        Returns (enrollment_code, remaining_name)
        """
        match = re.search(cls.ENROLLMENT_CODE_PATTERN, course_name, re.IGNORECASE)
        if match:
            enrollment_code = f"ENROLL/{match.group(2)}-{match.group(3)}/{match.group(4)}"
            remaining = re.sub(cls.ENROLLMENT_CODE_PATTERN, '', course_name, flags=re.IGNORECASE).strip()
            return enrollment_code, remaining
            
        return None, course_name
    
    @classmethod
    def extract_course_metadata(cls, course_name: str) -> Dict[str, Optional[str]]:
        """
        Extract all metadata from a course name.
        """
        metadata = {}
        remaining = course_name
        
        # Extract enrollment code first (if present)
        enrollment_code, remaining = cls.extract_enrollment_code(remaining)
        if enrollment_code:
            metadata['enrollment_code'] = enrollment_code
        
        # Extract institution
        institution, remaining = cls.extract_institution_from_name(remaining)
        if institution:
            metadata['institution'] = institution
        
        # Extract program type
        program_type, remaining = cls.extract_program_type(remaining)
        if program_type:
            metadata['program_type'] = program_type
        
        # Extract term/semester if present
        term_match = re.search(r'(Spring|Summer|Fall|Winter)\s*(\d{4})', remaining, re.IGNORECASE)
        if term_match:
            metadata['term'] = f"{term_match.group(1)} {term_match.group(2)}"
            remaining = remaining.replace(term_match.group(0), '').strip()
        
        # Extract section number if present
        section_match = re.search(r'Section\s*(\d+|[A-Z])', remaining, re.IGNORECASE)
        if section_match:
            metadata['section'] = section_match.group(1)
            remaining = remaining.replace(section_match.group(0), '').strip()
        
        # Clean up remaining name
        remaining = re.sub(r'\s+', ' ', remaining).strip()  # Multiple spaces to single
        remaining = re.sub(r'^[-:,]\s*', '', remaining).strip()  # Leading separators
        remaining = re.sub(r'\s*[-:,]$', '', remaining).strip()  # Trailing separators
        
        if remaining:
            metadata['course_title'] = remaining
            
        return metadata
    
    @classmethod
    def normalize_course_name(cls, course_name: str, source: str = 'canvas') -> str:
        """
        Normalize a course name to standard format: "Institution - Program Name"
        
        Args:
            course_name: Original course name from Canvas or Zoho
            source: Data source ('canvas' or 'zoho')
            
        Returns:
            Normalized course name in format "Institution - Program Name"
        """
        if not course_name:
            return course_name
            
        # Extract metadata
        metadata = cls.extract_course_metadata(course_name)
        
        # Build normalized name
        parts = []
        
        # Add institution if found
        if metadata.get('institution'):
            parts.append(metadata['institution'])
        
        # Build program/course part
        program_parts = []
        
        if metadata.get('program_type'):
            program_parts.append(metadata['program_type'])
        elif metadata.get('course_title'):
            program_parts.append(metadata['course_title'])
        
        # Add term if present
        if metadata.get('term'):
            program_parts.append(f"({metadata['term']})")
        
        # Add section if present and relevant
        if metadata.get('section'):
            program_parts.append(f"Section {metadata['section']}")
        
        if program_parts:
            parts.append(' '.join(program_parts))
        
        # If we have both institution and program, join with " - "
        if len(parts) == 2:
            return f"{parts[0]} - {parts[1]}"
        elif len(parts) == 1:
            return parts[0]
        else:
            # Fallback to original name if we couldn't parse it
            return course_name
    
    @classmethod
    def generate_course_id(cls, course_name: str, canvas_id: Optional[str] = None, 
                          zoho_id: Optional[str] = None) -> str:
        """
        Generate a consistent course ID from various inputs.
        """
        metadata = cls.extract_course_metadata(course_name)
        
        # Build ID components
        id_parts = []
        
        # Add enrollment code if present
        if metadata.get('enrollment_code'):
            # Clean enrollment code for ID
            code = metadata['enrollment_code'].replace('/', '_').replace('-', '_')
            id_parts.append(code)
        elif metadata.get('institution'):
            # Use institution abbreviation
            for abbr, full_name in cls.INSTITUTION_MAPPINGS.items():
                if full_name == metadata['institution']:
                    id_parts.append(abbr)
                    break
            else:
                # Create abbreviation from institution name
                words = metadata['institution'].split()
                abbr = ''.join(w[0].upper() for w in words if w[0].isalpha())
                id_parts.append(abbr)
        
        # Add program type identifier
        if metadata.get('program_type'):
            if 'Strategic Artificial Intelligence' in metadata['program_type']:
                id_parts.append('AI')
            elif 'Women in Leadership' in metadata['program_type']:
                id_parts.append('WIL')
            elif 'Executive Education' in metadata['program_type']:
                id_parts.append('EE')
            else:
                # Create abbreviation
                words = metadata['program_type'].split()
                abbr = ''.join(w[0].upper() for w in words[:3] if w[0].isalpha())
                id_parts.append(abbr)
        
        # Add term if present
        if metadata.get('term'):
            term_parts = metadata['term'].split()
            if len(term_parts) == 2:
                # e.g., "Fall 2024" -> "F24"
                season = term_parts[0][0].upper()
                year = term_parts[1][-2:]
                id_parts.append(f"{season}{year}")
        
        # Fallback to Canvas/Zoho IDs if no good ID generated
        if not id_parts:
            if canvas_id:
                id_parts.append(f"CANVAS_{canvas_id}")
            elif zoho_id:
                id_parts.append(f"ZOHO_{zoho_id}")
            else:
                # Last resort: use sanitized course name
                sanitized = re.sub(r'[^A-Za-z0-9]+', '_', course_name)[:30]
                id_parts.append(sanitized.upper())
        
        return '_'.join(id_parts)