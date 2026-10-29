
"use client";

import { useState } from "react";

export default function SubmitComplaintPage() {
    const [description, setDescription] = useState("");
    const [location, setLocation] = useState("");
    const [predictedCategory, setPredictedCategory] = useState("");
    const [duplicateInfo, setDuplicateInfo] = useState<{
        is_duplicate: boolean;
        similarity_score: number;
    } | null>(null);
    const [submitted, setSubmitted] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    async function handleSubmit(
        event: React.FormEvent<HTMLFormElement>
    ) {
        event.preventDefault();

        setIsSubmitting(true);
        setErrorMessage("");

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/complaints`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        description,
                        location,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail
                        ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail))
                        : "Failed to submit complaint."
                );
            }

            setPredictedCategory(data.predicted_category || "");
            if (
                data.duplicate_detection &&
                typeof data.duplicate_detection.is_duplicate === "boolean" &&
                typeof data.duplicate_detection.similarity_score === "number" &&
                Number.isFinite(data.duplicate_detection.similarity_score)
            ) {
                setDuplicateInfo({
                    is_duplicate: data.duplicate_detection.is_duplicate,
                    similarity_score: data.duplicate_detection.similarity_score,
                });
            } else {
                setDuplicateInfo(null);
            }
            setSubmitted(true);
        } catch (error) {
            console.error("Complaint submission error:", error);

            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "Unable to connect to the backend. Please try again."
            );
        } finally {
            setIsSubmitting(false);
        }
    }

    function resetForm() {
        setDescription("");
        setLocation("");
        setPredictedCategory("");
        setDuplicateInfo(null);
        setSubmitted(false);
        setErrorMessage("");
    }

    return (
        <main className="min-h-screen bg-slate-50 px-5 py-12 text-slate-900">
            <div className="mx-auto max-w-2xl">
                <a
                    href="/"
                    className="text-sm font-medium text-blue-700 hover:underline"
                >
                    ← Back to Home
                </a>

                <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-9">
                    <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">
                        Citizen Portal
                    </p>

                    <h1 className="mt-2 text-3xl font-bold">
                        Report a Civic Issue
                    </h1>

                    <p className="mt-3 text-slate-600">
                        Describe the problem so it can be reviewed and routed to the
                        appropriate department.
                    </p>

                    {submitted ? (
                        <div className="mt-8 rounded-xl border border-green-200 bg-green-50 p-5">
                            <h2 className="text-xl font-bold text-green-800">
                                Complaint received successfully!
                            </h2>

                            {predictedCategory && (
                                <p className="mt-2 text-green-900">
                                    <span className="font-semibold">Predicted Category:</span>{" "}
                                    <span className="inline-block rounded-md bg-green-200 px-2 py-0.5 text-sm font-bold text-green-900">
                                        {predictedCategory}
                                    </span>
                                </p>
                            )}

                            {duplicateInfo &&
                                duplicateInfo.is_duplicate === true &&
                                Number.isFinite(duplicateInfo.similarity_score) &&
                                duplicateInfo.similarity_score >= 0 &&
                                duplicateInfo.similarity_score <= 1 && (
                                    <div
                                        role="alert"
                                        className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
                                    >
                                        <p className="font-semibold text-amber-950">
                                            ⚠️ Possible duplicate detected
                                        </p>
                                        <p className="mt-1">
                                            A very similar complaint was recently reported in our system (
                                            {(duplicateInfo.similarity_score * 100).toFixed(0)}% text similarity).
                                        </p>
                                        <p className="mt-1 text-xs text-amber-800">
                                            Text similarity indicates phrasing resemblance, not proof of the same real-world incident. Your complaint was still successfully recorded.
                                        </p>
                                    </div>
                                )}

                            <p className="mt-2 text-green-900">
                                Your complaint has been successfully submitted and saved to
                                our database. Thank you for helping improve your community.
                            </p>

                            <button
                                type="button"
                                onClick={resetForm}
                                className="mt-4 rounded-lg bg-green-700 px-4 py-2 font-semibold text-white hover:bg-green-800"
                            >
                                Submit Another Complaint
                            </button>
                        </div>
                    ) : (
                        <form
                            onSubmit={handleSubmit}
                            className="mt-8 space-y-6"
                        >
                            <div>
                                <label
                                    htmlFor="description"
                                    className="mb-2 block font-semibold"
                                >
                                    Describe the issue
                                </label>

                                <textarea
                                    id="description"
                                    required
                                    minLength={10}
                                    maxLength={1000}
                                    rows={5}
                                    value={description}
                                    onChange={(event) => {
                                        setDescription(event.target.value);
                                        setErrorMessage("");
                                    }}
                                    placeholder="Example: A large pothole near the bus stop is filling with water and causing two-wheelers to slip."
                                    className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                                />

                                <p className="mt-1 text-right text-sm text-slate-500">
                                    {description.length}/1000 characters
                                </p>
                            </div>


                            <div>
                                <label
                                    htmlFor="location"
                                    className="mb-2 block font-semibold"
                                >
                                    Location of the issue
                                </label>

                                <input
                                    id="location"
                                    required
                                    maxLength={200}
                                    value={location}
                                    onChange={(event) => {
                                        setLocation(event.target.value);
                                        setErrorMessage("");
                                    }}
                                    placeholder="Example: Near the main bus stand"
                                    className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                                />
                            </div>

                            {errorMessage && (
                                <div
                                    role="alert"
                                    className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"
                                >
                                    <p className="font-semibold">
                                        Complaint submission failed
                                    </p>
                                    <p className="mt-1">{errorMessage}</p>
                                    <p className="mt-2">
                                        Please check that your backend server is running
                                        and try again.
                                    </p>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="w-full rounded-xl bg-blue-700 px-5 py-4 font-semibold text-white shadow-sm transition hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {isSubmitting
                                    ? "Sending Complaint..."
                                    : "Submit Complaint →"}
                            </button>

                            <p className="text-center text-xs text-slate-500">
                                Prototype only: complaints are saved in the project
                                database for testing and are not sent to
                                a government department.
                            </p>
                        </form>
                    )}
                </div>
            </div>
        </main>
    );
}
