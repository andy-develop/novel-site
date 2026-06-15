/// <reference types="astro/client" />
/// <reference types="@astrojs/cloudflare" />

interface Env {
  R2_BUCKET: R2Bucket;
}

declare namespace App {
  interface Locals {
    runtime: {
      env: Env;
    };
  }
}
