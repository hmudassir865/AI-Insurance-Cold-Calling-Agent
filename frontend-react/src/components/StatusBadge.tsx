import clsx from "clsx";

interface StatusBadgeProps {
  status: string;
}

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
  interested: "bg-green-100 text-green-800 border-green-200",
  not_interested: "bg-red-100 text-red-800 border-red-200",
  callback: "bg-blue-100 text-blue-800 border-blue-200",
  busy: "bg-purple-100 text-purple-800 border-purple-200",
  completed: "bg-green-100 text-green-800 border-green-200",
  active: "bg-green-100 text-green-800 border-green-200",
  draft: "bg-gray-100 text-gray-800 border-gray-200",
  paused: "bg-yellow-100 text-yellow-800 border-yellow-200",
  failed: "bg-red-100 text-red-800 border-red-200",
  initiated: "bg-blue-100 text-blue-800 border-blue-200",
  ringing: "bg-indigo-100 text-indigo-800 border-indigo-200",
  answered: "bg-green-100 text-green-800 border-green-200",
  "no-answer": "bg-gray-100 text-gray-800 border-gray-200",
  new: "bg-blue-100 text-blue-800 border-blue-200",
  contacted: "bg-purple-100 text-purple-800 border-purple-200",
  qualified: "bg-amber-100 text-amber-800 border-amber-200",
  converted: "bg-emerald-100 text-emerald-800 border-emerald-200",
  lost: "bg-red-100 text-red-800 border-red-200",
  wrong_number: "bg-gray-100 text-gray-800 border-gray-200",
  dnc: "bg-gray-100 text-gray-800 border-gray-200",
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const colorClass = statusColors[status] ?? "bg-gray-100 text-gray-800 border-gray-200";

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
        colorClass,
      )}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}
