import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { useAuth } from "../contexts/AuthContext";

interface HeaderNavProps {}

export function HeaderNav({}: HeaderNavProps) {
  const { user } = useAuth();
  const unreadNotifications = 2;

  const handleNotificationClick = () => {
    console.log("Notifications clicked");
  };

  const handleSettingsClick = () => {
    console.log("Settings clicked");
  };

  return (
    <header className="h-20 border-b bg-white">
      <div className="flex h-full items-center justify-between px-6">
        {/* Brand Section */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div>
              <h1 className="text-xl font-semibold">
                Course Feedback Intelligence
              </h1>
            </div>
          </div>
        </div>

        {/* User Actions */}
        <div className="flex items-center gap-2">
          {user && (
            // Authenticated user menu
            <>
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
            </>
          )}
        </div>
      </div>
    </header>
  );
}