import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

export default definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {
        surface: {
          950: "#183240",
        },
      },
      dark: {
        surface: {
          950: "#183240",
        },
      },
    },
  },

  components: {
    card: {
      colorScheme: {
        dark: {
          root: {
            color: "{gray.50}",
          },

          body: {},
        },

        light: {
          root: {
            color: "{gray.900}",
          },
        },
      },
    },

    toast: {
      root: {
        width: "325px",
      },
    },
  },
});
