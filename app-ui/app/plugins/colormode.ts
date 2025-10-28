class ColorModeBootstrap {
  constructor() {}

  public setStoredTheme(theme: string) {
    localStorage.setItem("theme", theme);
  }

  public getStoredTheme() {
    return localStorage.getItem("theme") || "auto";
  }

  public setTheme(theme: string) {
    if (theme === "auto") {
      document.documentElement.setAttribute(
        "data-bs-theme",
        window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
      );
    } else {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }
  }

  public getPreferredTheme() {
    const storedTheme = this.getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }

    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  public showActiveTheme(theme: string, focus = false) {
    const themeSwitcher = document.querySelector("#bd-theme");

    if (!themeSwitcher) {
      return;
    }

    const themeSwitcherText = document.querySelector("#bd-theme-text");
    const activeThemeIcon = document.querySelector(".theme-icon-active use");
    const btnToActive = document.querySelector(`[data-bs-theme-value="${theme}"]`);
    const svgOfActiveBtn = btnToActive?.querySelector("svg use")?.getAttribute("href");

    document.querySelectorAll("[data-bs-theme-value]").forEach((element) => {
      element.classList.remove("active");
      element.setAttribute("aria-pressed", "false");
    });

    btnToActive?.classList.add("active");
    btnToActive?.setAttribute("aria-pressed", "true");
    activeThemeIcon?.setAttribute("href", svgOfActiveBtn as string);
    const themeSwitcherLabel = `${themeSwitcherText?.textContent} (${(btnToActive as HTMLElement | null)?.dataset.bsThemeValue})`;
    themeSwitcher.setAttribute("aria-label", themeSwitcherLabel);

    if (focus) {
      themeSwitcher.focus();
    }
  }

  public async setup() {
    if (document) {
      (() => {
        this.setTheme(this.getPreferredTheme());

        window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
          const storedTheme = this.getStoredTheme();
          if (storedTheme !== "light" && storedTheme !== "dark") {
            this.setTheme(this.getPreferredTheme());
          }
        });

        window.addEventListener("DOMContentLoaded", () => {
          this.showActiveTheme(this.getPreferredTheme());

          document.querySelectorAll("[data-bs-theme-value]").forEach((toggle) => {
            toggle.addEventListener("click", () => {
              const theme: string = toggle.getAttribute("data-bs-theme-value") as string;
              this.setStoredTheme(theme);
              this.setTheme(theme);
              this.showActiveTheme(theme, true);
            });
          });
        });
      })();
    }
  }
}

export default defineNuxtPlugin(() => {
  return {
    provide: {
      colormode: new ColorModeBootstrap(),
      name: "colormode",
      async setup() {
        return await this.colormode.setup();
      },
    },
  };
});
