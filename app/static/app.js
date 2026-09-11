let lastVersion = -1;

async function fetchFragment() {
  const sessionId = window.sessionId;
  const participantId = window.participantId;

  try {
    const response = await fetch(`/sessions/${sessionId}/fragment`);
    if (!response.ok) {
      console.error("Failed to fetch fragment:", response.status);
      return;
    }

    const html = await response.text();
    const container = document.getElementById("items-container");

    // Preserve open/closed state of the breakdown <details> across re-renders,
    // since replacing innerHTML would otherwise always reset it to closed.
    const wasBreakdownOpen = container.querySelector("details")?.open ?? false;

    container.innerHTML = html;

    const breakdownDetails = container.querySelector("details");
    if (breakdownDetails) {
      breakdownDetails.open = wasBreakdownOpen;
    }

    // Re-attach event listeners after DOM update
    attachFormListeners();
  } catch (error) {
    console.error("Error fetching fragment:", error);
  }
}

function attachFormListeners() {
  document.querySelectorAll(".claim-form").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const url = form.action;

      try {
        await fetch(url, {
          method: "POST",
          body: formData,
        });
        // Immediately fetch the updated fragment for responsive feedback
        fetchFragment();
      } catch (error) {
        console.error("Error submitting claim:", error);
      }
    });
  });
}

// Initial setup
attachFormListeners();
