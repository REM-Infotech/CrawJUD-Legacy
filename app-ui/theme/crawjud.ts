import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

export default definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {
        surface: {
          50: "{violet-eggplant.50}",
          100: "{violet-eggplant.100}",
          200: "{violet-eggplant.200}",
          300: "{violet-eggplant.300}",
          400: "{violet-eggplant.400}",
          500: "{violet-eggplant.500}",
          600: "{violet-eggplant.600}",
          700: "{violet-eggplant.700}",
          800: "{violet-eggplant.800}",
          900: "{violet-eggplant.900}",
          950: "{dark-950}",
        },
      },
      dark: {
        surface: {
          50: "{violet-eggplant.50}",
          100: "{violet-eggplant.100}",
          200: "{violet-eggplant.200}",
          300: "{violet-eggplant.300}",
          400: "{violet-eggplant.400}",
          500: "{violet-eggplant.500}",
          600: "{violet-eggplant.600}",
          700: "{violet-eggplant.700}",
          800: "{violet-eggplant.800}",
          900: "{violet-eggplant.900}",
          950: "{dark-950}",
        },
      },
    },
  },

  components: {
    card: {
      colorScheme: {
        dark: {
          root: {
            background: "{dark-950}",
            color: "{gray.50}",
          },

          body: {},
        },

        light: {
          root: {
            background: "{violet-eggplant.50}",
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
