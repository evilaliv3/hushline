function navController() {
  function setupDropdown() {
    const dropdownToggle = document.querySelector(".dropdown .dropbtn");
    if (!dropdownToggle) return;

    const dropdownContent = document.querySelector(".dropdown-content");
    const dropdownIcon = document.querySelector(".dropdown-icon");

    if (dropdownContent && dropdownIcon) {
      dropdownToggle.addEventListener("click", function (event) {
        event.preventDefault();
        dropdownContent.classList.toggle("show");
        dropdownContent.style.animation = dropdownContent.classList.contains(
          "show",
        )
          ? "fadeInSlideDown 0.3s ease forwards"
          : "fadeOutSlideUp 0.3s ease forwards";
        dropdownIcon.classList.toggle("rotate-icon");
        const expanded = this.getAttribute("aria-expanded") === "true" || false;
        this.setAttribute("aria-expanded", !expanded);
        dropdownContent.hidden = expanded;
      });

      window.addEventListener("click", function (event) {
        if (
          !dropdownToggle.contains(event.target) &&
          dropdownContent.classList.contains("show")
        ) {
          dropdownContent.classList.remove("show");
          dropdownIcon.classList.remove("rotate-icon");
          dropdownToggle.setAttribute("aria-expanded", "false");
          dropdownContent.hidden = true;
        }
      });
    }
  }

  function setupMobileNav() {
    const mobileNavToggle = document.querySelector(".mobileNav");
    const navList = document.querySelector("header nav ul");

    if (mobileNavToggle && navList) {
      mobileNavToggle.addEventListener("click", function (event) {
        event.preventDefault();
        navList.classList.toggle("show");
        const expanded = this.getAttribute("aria-expanded") === "true" || false;
        this.setAttribute("aria-expanded", !expanded);
      });
    }
  }

  setupDropdown();
  setupMobileNav();
}

document.addEventListener("DOMContentLoaded", function () {
  navController();

  function setupStatusForm() {
    const statusForm = document.getElementById("statusForm");
    if (!statusForm) return;

    const statusField = statusForm.querySelector('[name="status"]');
    if (statusField) {
      statusField.addEventListener("change", function () {
        const formData = new FormData(statusForm);

        fetch(statusForm.action, {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Failed to update status");
            }
            return response.text(); // Expecting the server to return HTML
          })
          .then((html) => {
            // Parse and update flash messages without reload
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const flashMessages = doc.querySelector(".flash-messages");
            if (flashMessages) {
              const existingFlash = document.querySelector(".flash-messages");
              if (existingFlash) {
                existingFlash.replaceWith(flashMessages);
              } else {
                document.body.insertBefore(
                  flashMessages,
                  document.body.firstChild,
                );
              }
            }
          })
          .catch((error) => {
            console.error("Error updating status:", error);
          });
      });
    }
  }

  setupStatusForm();

  function getCSSVariableValue(variableName) {
    // Fetch the CSS variable value directly from the :root element
    return getComputedStyle(document.documentElement)
      .getPropertyValue(variableName)
      .trim();
  }

  function updateThemeColor() {
    let themeColorMetaTag = document.querySelector('meta[name="theme-color"]');

    // Ensure the meta tag exists; create it if missing
    if (!themeColorMetaTag) {
      themeColorMetaTag = document.createElement("meta");
      themeColorMetaTag.setAttribute("name", "theme-color");
      document.head.appendChild(themeColorMetaTag);
    }

    // Fetch the CSS variables for light and dark mode
    const lightModeColor = getCSSVariableValue("--theme-color-light");
    const darkModeColor = getCSSVariableValue("--theme-color-dark");

    // Detect user preference for dark mode
    const isDarkMode = window.matchMedia(
      "(prefers-color-scheme: dark)",
    ).matches;

    // Set the appropriate color in the meta tag
    themeColorMetaTag.setAttribute(
      "content",
      isDarkMode ? darkModeColor : lightModeColor,
    );
  }

  // Initialize and add event listener for theme changes
  updateThemeColor();
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", updateThemeColor);

  // Handle user guidance
  const guidanceDiv = document.querySelector("#guidance-modal.modal");
  if (guidanceDiv) {
    let activePage = 0;

    const hasFinishedGuidance = localStorage.getItem("hasFinishedGuidance");
    if (!hasFinishedGuidance) {
      guidanceDiv.classList.add("show");

      // Count the child divs of guidanceDiv, these are the pages
      const guidancePages = guidanceDiv.querySelectorAll(":scope > div");
      const pagesCount = guidancePages.length;

      function showActivePage() {
        for (let i = 0; i < pagesCount; i++) {
          if (i == activePage) {
            guidancePages[i].classList.add("show");
            guidanceDiv
              .querySelectorAll(".page-bullet-" + i)
              .forEach((bullet) => {
                bullet.classList.add("active");
              });
          } else {
            guidancePages[i].classList.remove("show");
            guidanceDiv
              .querySelectorAll(".page-bullet-" + i)
              .forEach((bullet) => {
                bullet.classList.remove("active");
              });
          }
        }
      }

      function leaveClicked() {
        const exitButtonLink = document.querySelector(
          "#guidance-exit-button-link",
        );
        if (exitButtonLink) {
          const exitButtonLinkValue = exitButtonLink.value;
          try {
            const sanitizedUrl = new URL(exitButtonLinkValue);
            document.location.href = sanitizedUrl.href;
          } catch (e) {
            console.error("Invalid URL in exit button link:", exitButtonLinkValue);
          }
        } else {
          console.error("No exit button link found");
        }
      }

      function continueClicked() {
        if (activePage < pagesCount - 1) {
          activePage++;
          showActivePage();
        } else {
          console.error("No more pages to show");
        }
      }

      function backClicked() {
        if (activePage > 0) {
          activePage--;
          showActivePage();
        } else {
          console.error("No more pages to show");
        }
      }

      function doneClicked() {
        guidanceDiv.classList.remove("show");
        localStorage.setItem("hasFinishedGuidance", "true");
      }

      // If there are no pages, hide the modal and don't show it again
      if (pagesCount == 0) {
        guidanceDiv.classList.remove("show");
        localStorage.setItem("hasFinishedGuidance", "true");
      }

      // Choose which buttons should be shown, and also attach event listeners
      for (let i = 0; i < pagesCount; i++) {
        const page = guidancePages[i];

        const leaveButton = page.querySelector(".leave");
        if (leaveButton) {
          leaveButton.addEventListener("click", leaveClicked);
          leaveButton.classList.add("show");
        }

        // Show done on the last page
        if (i == pagesCount - 1) {
          const doneButton = page.querySelector(".done");
          if (doneButton) {
            doneButton.addEventListener("click", doneClicked);
            doneButton.classList.add("show");
          }
        }
        // Show continue on any non-last pages
        else {
          const continueButton = page.querySelector(".continue");
          if (continueButton) {
            continueButton.addEventListener("click", continueClicked);
            continueButton.classList.add("show");
          }
        }

        // She back on any non-first pages
        if (i > 0) {
          const backButton = page.querySelector(".back");
          if (backButton) {
            backButton.addEventListener("click", backClicked);
            backButton.classList.add("show");
          }
        }

        // Attach listener for the bullets
        guidanceDiv.querySelectorAll(".page-bullet-" + i).forEach((bullet) => {
          bullet.addEventListener("click", function () {
            activePage = i;
            showActivePage();
          });
        });
      }

      // Show the first page
      showActivePage();
    }
  }
});
