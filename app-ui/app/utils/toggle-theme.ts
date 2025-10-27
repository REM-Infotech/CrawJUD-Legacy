function toggleThemeMode(oldTheme: string, newTheme: string) {
  if (oldTheme === newTheme) return;
  document.documentElement.classList.remove(oldTheme);
  document.documentElement.classList.add(newTheme);
  document.body.setAttribute("data-theme", newTheme);
  sessionStorage.setItem("prime-theme", newTheme);
}

export function loadTheme({ firstTime = false } = {}) {
  let systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  let sessionTheme = sessionStorage.getItem("prime-theme");

  const currentdocumentTheme = document.documentElement.getAttribute("class");
  const currentBodyTheme = document.body.getAttribute("data-theme");

  if (!sessionTheme) {
    sessionTheme = systemTheme;
    sessionStorage.setItem("prime-theme", systemTheme);
  } else if (sessionTheme) {
    systemTheme = sessionTheme;
  }

  if (firstTime) {
    console.log("tema atual", {
      systemTheme,
      sessionTheme,
      currentBodyTheme,
      currentdocumentTheme,
    });
    if (systemTheme !== currentBodyTheme || systemTheme !== currentdocumentTheme) {
      console.log("troca de tema", { systemTheme, currentBodyTheme, currentdocumentTheme });
      toggleThemeMode(currentBodyTheme as string, systemTheme);
      toggleThemeMode(currentdocumentTheme as string, systemTheme);
    }
    return;
  } else {
    console.log(firstTime);
    toggleThemeMode(systemTheme, currentBodyTheme === "dark" ? "light" : "dark");
  }
}

loadTheme({ firstTime: true });
