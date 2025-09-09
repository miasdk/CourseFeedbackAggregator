import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { 
  Bell, 
  Settings, 
  Moon, 
  Sun,
  BarChart3
} from "lucide-react";

interface HeaderNavProps {
  onToggleTheme?: () => void;
  isDarkMode?: boolean;
}

export function HeaderNav({ onToggleTheme, isDarkMode = false }: HeaderNavProps) {
  const unreadNotifications = 2;

  const handleNotificationClick = () => {
    console.log("Notifications clicked");
  };

  const handleSettingsClick = () => {
    console.log("Settings clicked");
  };

  return (
    <header className="h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full items-center justify-between px-4">
        {/* Brand Section */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center">
              <BarChart3 className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-base font-medium">Course Feedback Intelligence</h1>
            </div>
          </div>
        </div>

        {/* User Actions */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <Button variant="ghost" size="sm" onClick={onToggleTheme}>
            {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative" onClick={handleNotificationClick}>
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

          {/* Settings */}
          <Button variant="ghost" size="sm" onClick={handleSettingsClick}>
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}