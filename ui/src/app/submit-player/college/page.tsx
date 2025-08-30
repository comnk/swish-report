"use client";

import Navigation from "@/components/navigation";
import { AlertCircle, ExternalLink } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SubmitPlayerPage() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: "",
    basketballReferenceLink: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus("idle");
    setErrorMessage("");

    try {
      const res = await fetch(
        "http://localhost:8000/college/prospects/submit-player",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: formData.name,
            basketball_reference_link: formData.basketballReferenceLink || null,
          }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Submission failed");
      }

      const data = await res.json();

      // ✅ redirect to new player page using returned player_uid
      router.push(`/high-school/${data.player_uid}`);
    } catch (err: unknown) {
      console.error(err);

      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("An unknown error occurred");
      }

      setSubmitStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = !!formData.name;

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

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {submitStatus === "error" && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <div>
              <h3 className="text-red-800 font-semibold">Submission Failed</h3>
              <p className="text-red-700 text-sm">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ExternalLink className="w-5 h-5 text-orange-600 mr-2" />
                Player Information
              </h2>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Full Name *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-black transition-colors"
                    placeholder="Enter player's full name"
                    required
                  />
                </div>

                <div>
                  <label
                    htmlFor="espnLink"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Basketball Reference Link
                  </label>
                  <input
                    type="url"
                    id="espnLink"
                    name="espnLink"
                    value={formData.basketballReferenceLink}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 text-black border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                    placeholder="https://www.sports-reference.com/cbb/players/..."
                  />
                </div>
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={!isFormValid || isSubmitting}
                  className="w-full bg-orange-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-orange-700 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Submitting...
                    </>
                  ) : (
                    "Submit Player"
                  )}
                </button>

                {!isFormValid && (
                  <p className="mt-2 text-sm text-gray-500 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    Please enter the player’s name
                  </p>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
