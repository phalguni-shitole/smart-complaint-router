
export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <nav className="flex items-center justify-between border-b bg-white px-6 py-5 md:px-12">
        <div>
          <h1 className="text-xl font-bold text-blue-800">
            Smart Complaint Router
          </h1>
          <p className="text-xs text-slate-500">
            AI-powered civic issue management
          </p>
        </div>
        <a
          href="#how-it-works"
          className="hidden rounded-lg px-4 py-2 font-medium text-blue-800 hover:bg-blue-50 sm:block"
        >
          How it works
        </a>
      </nav>

      <section className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-20 md:grid-cols-2 md:px-12 md:py-28">
        <div>
          <p className="mb-4 inline-block rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-800">
            A smarter way to report civic issues
          </p>

          <h2 className="text-4xl font-extrabold leading-tight tracking-tight md:text-6xl">
            Your city.
            <span className="block text-blue-700">Your voice.</span>
            <span className="block">Real action.</span>
          </h2>

          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
            Report potholes, water supply problems, broken streetlights and
            other civic issues. Our smart system helps categorize complaints,
            estimate urgency and route them to the right department.
          </p>

          <a
            href="/submit"
            className="mt-8 inline-flex items-center justify-center rounded-xl bg-blue-700 px-7 py-4 font-semibold text-white shadow-lg transition hover:bg-blue-800"
          >
            Report an Issue <span className="ml-2">→</span>
          </a>

          <p className="mt-3 text-sm text-slate-500">
            Simple reporting. Smarter routing. Better communities.
          </p>
        </div>

        <div className="rounded-3xl bg-blue-900 p-8 text-white shadow-xl md:p-10">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-200">
            The smarter workflow
          </p>
          <h3 className="mt-4 text-3xl font-bold">
            From complaint to action
          </h3>

          <div className="mt-8 space-y-4">
            {[
              {
                number: "01",
                title: "Describe the issue",
                description: "Explain the problem in your own words.",
              },
              {
                number: "02",
                title: "AI-assisted analysis",
                description: "Suggest a category and priority level.",
              },
              {
                number: "03",
                title: "Route and track",
                description: "Send it to the relevant department and follow progress.",
              },
            ].map((step) => (
              <div
                key={step.number}
                className="flex gap-4 rounded-xl border border-white/15 bg-white/10 p-4"
              >
                <span className="font-bold text-blue-200">{step.number}</span>
                <div>
                  <h4 className="font-semibold">{step.title}</h4>
                  <p className="mt-1 text-sm leading-6 text-blue-100">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section
        id="how-it-works"
        className="border-t bg-white px-6 py-16 md:px-12"
      >
        <div className="mx-auto max-w-6xl">
          <div className="text-center">
            <h3 className="text-3xl font-bold">One platform, multiple solutions</h3>
            <p className="mt-3 text-slate-600">
              Designed to make civic complaint handling clearer and more organized.
            </p>
          </div>

          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: "🛣️",
                title: "Smart categorization",
                description: "Help identify the department responsible for an issue.",
              },
              {
                icon: "🚦",
                title: "Priority estimation",
                description: "Highlight potentially urgent problems for review.",
              },
              {
                icon: "🔎",
                title: "Duplicate detection",
                description: "Help identify similar complaints about the same issue.",
              },
              {
                icon: "📍",
                title: "Status tracking",
                description: "Make complaint progress easier to follow.",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="rounded-2xl border border-slate-200 bg-slate-50 p-6 transition hover:-translate-y-1 hover:shadow-md"
              >
                <span className="text-3xl">{feature.icon}</span>
                <h4 className="mt-4 font-bold">{feature.title}</h4>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t px-6 py-6 text-center text-sm text-slate-500">
        Smart Complaint Router · Student AI/ML project prototype
      </footer>
    </main>
  );
}
