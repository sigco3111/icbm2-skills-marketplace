// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://sigco3111.github.io',
  base: '/icbm2-skills-marketplace',
  output: 'static',
  vite: {
    plugins: [tailwindcss()]
  }
});
