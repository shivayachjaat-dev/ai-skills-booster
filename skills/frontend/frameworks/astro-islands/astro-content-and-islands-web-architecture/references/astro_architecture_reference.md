# Astro Architecture & Performance Guidelines

## Islands Architecture Philosophy
Astro pioneered the Islands Architecture paradigm for web development. In this paradigm:
- The base HTML document is 100% static, pre-rendered during build or on the server edge.
- Interactive components are isolated widgets embedded in the document slot.
- JavaScript runtime is strictly downloaded and executed when the specified trigger condition is satisfied.

## Performance Checklist
1. **Fonts & Assets**: Always use `@astrojs/image` or native Astro `<Image />` component with automated WebP conversion and `srcset` attributes.
2. **SSR Adapters**: When switching from SSG to SSR, select the appropriate official adapter:
   - `@astrojs/node` for standalone Node.js container environments.
   - `@astrojs/cloudflare` for zero-cold-start edge workers.
   - `@astrojs/vercel` for serverless Lambdas.
3. **Cross-Island Communication**:
   Use Nano Stores for lightweight (<1kb), framework-agnostic shared state:
   ```typescript
   import { atom } from 'nanostores';
   export const isCartOpen = atom(false);
   ```
