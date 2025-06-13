import { useEffect, useState } from "react";

interface DigitalClockProps {
  timezone?: string;
}

function DigitalClock({ timezone = "UTC" }: DigitalClockProps) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) =>
    new Intl.DateTimeFormat("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZone: timezone,
    }).format(date);

  return (
    <div className="flex items-center justify-center p-2">
      <div className="rounded-lg">
        <div className="text-md font-mono font-bold text-primary">
          {formatTime(time)} {timezone}
        </div>
      </div>
    </div>
  );
}

export default DigitalClock;
