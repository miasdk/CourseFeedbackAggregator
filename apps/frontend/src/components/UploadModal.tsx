import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, File, CheckCircle, AlertCircle } from 'lucide-react';
import { Course } from '../types';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadComplete?: (courses: Course[]) => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState(0);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  };

  const handleFiles = async (files: File[]) => {
    const csvFiles = files.filter(file => file.name.endsWith('.csv'));
    
    if (csvFiles.length === 0) {
      setUploadStatus('error');
      return;
    }

    // Simulate upload process
    setUploadStatus('uploading');
    for (let i = 0; i <= 100; i += 10) {
      setProgress(i);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    setUploadStatus('success');
    
    // Simulate parsing uploaded courses
    const uploadedCourses: Course[] = csvFiles.map((file, index) => ({
      id: `uploaded-${Date.now()}-${index}`,
      title: `Course from ${file.name}`,
      category: 'Technology',
      rating: 4.0 + Math.random(),
      reviewCount: Math.floor(Math.random() * 100) + 50,
      moduleCount: Math.floor(Math.random() * 12) + 6,
      lastUpdated: 'Just uploaded',
      lastUpdatedDate: new Date(),
      criticalIssues: Math.floor(Math.random() * 3),
      description: `Course data imported from ${file.name}`,
      instructor: 'Imported Data',
      duration: `${Math.floor(Math.random() * 8) + 4} weeks`
    }));

    if (onUploadComplete) {
      onUploadComplete(uploadedCourses);
    }

    setTimeout(() => {
      onClose();
      setUploadStatus('idle');
      setProgress(0);
    }, 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-3xl shadow-apple-xl p-8 max-w-lg w-full"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-apple-900">
                Upload Course Data
              </h2>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full hover:bg-apple-100 flex items-center justify-center transition-colors"
              >
                <X className="w-5 h-5 text-apple-600" />
              </button>
            </div>

            {/* Upload Area */}
            <div
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200 ${
                isDragging
                  ? 'border-blue-400 bg-blue-50'
                  : uploadStatus === 'success'
                  ? 'border-green-400 bg-green-50'
                  : uploadStatus === 'error'
                  ? 'border-red-400 bg-red-50'
                  : 'border-apple-300 hover:border-blue-400 hover:bg-blue-50'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {uploadStatus === 'idle' && (
                <>
                  <Upload className="w-12 h-12 text-apple-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-apple-900 mb-2">
                    Drop your CSV files here
                  </h3>
                  <p className="text-apple-600 mb-4">
                    or click to browse files
                  </p>
                  <input
                    type="file"
                    accept=".csv"
                    multiple
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="btn-primary cursor-pointer inline-flex items-center space-x-2"
                  >
                    <File className="w-5 h-5" />
                    <span>Choose Files</span>
                  </label>
                </>
              )}

              {uploadStatus === 'uploading' && (
                <div className="space-y-4">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto"
                  >
                    <Upload className="w-6 h-6 text-white" />
                  </motion.div>
                  <h3 className="text-lg font-medium text-apple-900">
                    Processing files...
                  </h3>
                  <div className="w-full bg-apple-200 rounded-full h-2">
                    <motion.div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${progress}%` }}
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.2 }}
                    />
                  </div>
                  <p className="text-apple-600">{progress}% complete</p>
                </div>
              )}

              {uploadStatus === 'success' && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="space-y-4"
                >
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
                  <h3 className="text-lg font-medium text-green-900">
                    Upload successful!
                  </h3>
                  <p className="text-green-700">
                    Your course data has been processed and is now available in the dashboard.
                  </p>
                </motion.div>
              )}

              {uploadStatus === 'error' && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="space-y-4"
                >
                  <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
                  <h3 className="text-lg font-medium text-red-900">
                    Upload failed
                  </h3>
                  <p className="text-red-700">
                    Please make sure you're uploading CSV files only.
                  </p>
                  <button
                    onClick={() => setUploadStatus('idle')}
                    className="btn-primary"
                  >
                    Try Again
                  </button>
                </motion.div>
              )}
            </div>

            {/* File Requirements */}
            <div className="mt-6 p-4 bg-apple-50 rounded-xl">
              <h4 className="font-medium text-apple-900 mb-2">File Requirements:</h4>
              <ul className="text-sm text-apple-600 space-y-1">
                <li>• CSV format only</li>
                <li>• Maximum file size: 10MB</li>
                <li>• Multiple files supported</li>
                <li>• Course review data format</li>
              </ul>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default UploadModal; 