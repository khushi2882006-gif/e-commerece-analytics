export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-32 text-red-500 text-sm">
      ⚠️ {message}
    </div>
  )
}
