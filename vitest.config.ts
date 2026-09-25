import {defineConfig} from 'vitest/config';
export default defineConfig({test:{include:['frontend/tests/**/*.test.ts'],coverage:{provider:'v8',include:['frontend/src/logic.ts'],reporter:['json','json-summary','text'],reportsDirectory:'artifacts/frontend-coverage'}}});
