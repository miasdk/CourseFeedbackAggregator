import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

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
            <div>
              <h1 className="text-lg font-semibold">Course Feedback Intelligence</h1>
            </div>
          </div>
        </div>

        {/* User Actions */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <Button variant="ghost" size="sm" onClick={onToggleTheme}>
            {isDarkMode ? "Light" : "Dark"}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative" onClick={handleNotificationClick}>
            Notifications
            {unreadNotifications > 0 && (
              <Badge 
                variant="destructive" 
                className="ml-1 h-4 px-1 text-xs"
              >
                {unreadNotifications}
              </Badge>
            )}
          </Button>

          {/* Settings */}
          <Button variant="ghost" size="sm" onClick={handleSettingsClick}>
            Settings
          </Button>
        </div>
      </div>
    </header>
  );
}