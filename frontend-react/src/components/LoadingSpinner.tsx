import { Circle } from "lucide-react";

export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-20">
      <Circle size={32} className="animate-spin text-blue-600" />
      <p className="text-sm font-medium text-gray-500">Loading...</p>
    </div>
  );
}
