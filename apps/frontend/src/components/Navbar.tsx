import { Button } from "./ui/button";
import { useAuth } from "../contexts/AuthContext";

interface NavbarProps {
  onSignInClick?: () => void;
}

export function Navbar({ onSignInClick }: NavbarProps) {
  const { user, signOut } = useAuth();

  return (
    <nav className="h-12 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full items-center justify-between px-4">
        <div className="flex items-center">
          {/* Left side - can add logo or brand name if needed */}
        </div>

        <div className="flex items-center gap-2">
          {user ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                {user.email}
              </span>
              <Button variant="outline" size="sm" onClick={() => signOut()}>
                Sign Out
              </Button>
            </div>
          ) : (
            <Button variant="default" size="sm" onClick={onSignInClick}>
              Sign In
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}