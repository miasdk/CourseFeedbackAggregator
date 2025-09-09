/**
 * Simplified Header Navigation Component
 * 
 * Clean, professional header with minimal visual clutter
 * for the Course Improvement Prioritization System
 */

import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "./ui/dropdown-menu";
import { 
  Bell, 
  Settings, 
  User, 
  LogOut, 
  Moon, 
  Sun,
  BarChart3
} from "lucide-react";
import { toast } from "sonner@2.0.3";

interface HeaderNavProps {
  onToggleTheme?: () => void;
  isDarkMode?: boolean;
}

/**
 * Simplified header focusing on essential navigation elements
 * Removes visual clutter while maintaining professional appearance
 */
export function HeaderNav({ onToggleTheme, isDarkMode = false }: HeaderNavProps) {
  const unreadNotifications = 2; // Mock data

  const handleNotificationClick = () => {
    toast.info("Notifications panel will be available in the next release");
  };

  const handleProfileAction = (action: string) => {
    toast.info(`${action} functionality will be available in the next release`);
  };

  return (
    <header className="h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full items-center justify-between px-4">
        {/* Brand Section - Simplified */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center">
              <BarChart3 className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-base font-medium">Course Prioritization</h1>
            </div>
          </div>
        </div>

        {/* User Actions - Minimal */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <Button variant="ghost" size="sm" onClick={onToggleTheme}>
            {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-4 w-4" />
                {unreadNotifications > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 h-4 w-4 rounded-full p-0 text-xs flex items-center justify-center"
                  >
                    {unreadNotifications}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <div className="p-3">
                <h4 className="text-sm font-medium mb-2">Recent Updates</h4>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>Canvas sync completed successfully</p>
                  <p>3 new critical issues detected</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="w-full mt-2" 
                  onClick={handleNotificationClick}
                >
                  View All
                </Button>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/api/placeholder/32/32" alt="User" />
                  <AvatarFallback>SC</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48" align="end">
              <div className="p-2">
                <p className="text-sm font-medium">Sarah Chen</p>
                <p className="text-xs text-muted-foreground">Administrator</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleProfileAction("Profile")}>
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleProfileAction("Settings")}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleProfileAction("Sign out")}>
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}