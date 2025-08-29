import Navigation from "@/components/navigation";

export default function SubmitPlayerPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Submit Missing College Player
            </h1>
            <p className="mt-2 text-gray-600 max-w-2xl mx-auto">
              Help us expand our database by submitting information about high
              school players who aren&apos;t currently in our system.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
