import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

export default definePreset(Aura, {
  semantic: {
    colorScheme: {
      light: {
        surface: {
          50: "{violet.50}",
          100: "{violet.100}",
          200: "{violet.200}",
          300: "{violet.300}",
          400: "{violet.400}",
          500: "{violet.500}",
          600: "{violet.600}",
          700: "{violet.700}",
          800: "{violet.800}",
          900: "{violet.900}",
          950: "{violet.950}",
        },
      },
      dark: {
        surface: {
          50: "{violet.50}",
          100: "{violet.100}",
          200: "{violet.200}",
          300: "{violet.300}",
          400: "{violet.400}",
          500: "{violet.500}",
          600: "{violet.600}",
          700: "{violet.700}",
          800: "{violet.800}",
          900: "{violet.900}",
          950: "{violet.950}",
        },
      },
    },
  },

  components: {
    card: {
      colorScheme: {
        dark: {
          root: {
            background: "{violet.950}",
            color: "{gray.50}",
          },

          body: {},
        },

        light: {
          root: {
            background: "{violet.50}",
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
