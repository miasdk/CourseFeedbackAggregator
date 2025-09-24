import { Button } from "./ui/button";
import { useAuth } from "../contexts/AuthContext";
import { BarChart3, BookOpen, Settings } from "lucide-react";

interface NavbarProps {
  onSignInClick?: () => void;
}

export function Navbar({ onSignInClick }: NavbarProps) {
  const { user, signOut } = useAuth();

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="h-16 px-6">
        <div className="flex h-full items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-sm">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">Course Feedback</h1>
                <p className="text-xs text-gray-500 -mt-0.5">Intelligence Platform</p>
              </div>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center gap-1">
              <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Dashboard
              </button>
              <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Courses
              </button>
              <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Analytics
              </button>
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-3">
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
              <Settings className="w-5 h-5" />
            </button>
            
            {user ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-gray-900">{user.email?.split('@')[0]}</p>
                  <p className="text-xs text-gray-500">Administrator</p>
                </div>
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-sm">
                  {user.email?.[0]?.toUpperCase()}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => signOut()}
                  className="ml-2 text-gray-600 border-gray-300 hover:bg-gray-50"
                >
                  Sign Out
                </Button>
              </div>
            ) : (
              <Button 
                onClick={onSignInClick}
                className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 text-sm font-medium"
              >
                Sign In
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}