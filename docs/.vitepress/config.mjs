import { defineConfig } from "vitepress";
import { sidebar_content } from "./sidebar.mjs";

export default defineConfig({
  base: "/adaptive-phase-field-fracture/",
  title: "Adaptive Phase-Field Fracture",
  description:
    "Adaptive phase-field fracture: notes, examples, and research-grade implementations.",

  lastUpdated: false,

  markdown: {
    math: true,
  },

  head: [
    // Basic metadata
    [
      "meta",
      {
        name: "description",
        content:
          "Adaptive phase-field fracture methods with notes, examples, and reproducible research workflows.",
      },
    ],
    ["meta", { name: "author", content: "Abhinav Gupta" }],

    // Open Graph
    [
      "meta",
      { property: "og:title", content: "Adaptive Phase-Field Fracture" },
    ],
    [
      "meta",
      {
        property: "og:description",
        content:
          "Research notes and examples on adaptive phase-field fracture, adaptivity, and HPC.",
      },
    ],
    ["meta", { property: "og:type", content: "website" }],
    [
      "meta",
      {
        property: "og:url",
        content: "https://iitrabhi.github.io/adaptive-phase-field-fracture/",
      },
    ],
    [
      "meta",
      {
        property: "og:image",
        content: "/adaptive-phase-field-fracture/logos/og-image.png",
      },
    ],

    // Twitter cards
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
    [
      "meta",
      {
        name: "twitter:title",
        content: "Adaptive Phase-Field Fracture",
      },
    ],
    [
      "meta",
      {
        name: "twitter:description",
        content:
          "Notes and examples on adaptive phase-field fracture and large-scale simulations.",
      },
    ],
    [
      "meta",
      {
        name: "twitter:image",
        content: "/adaptive-phase-field-fracture/logos/og-image.png",
      },
    ],

    // Favicons
    [
      "link",
      {
        rel: "apple-touch-icon",
        sizes: "196x196",
        href: "/adaptive-phase-field-fracture/logos/favicon-196x196.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        href: "/adaptive-phase-field-fracture/logos/favicon-32x32.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        href: "/adaptive-phase-field-fracture/logos/favicon-16x16.png",
      },
    ],
  ],

  themeConfig: {
    logo: "/logos/logo.svg",
    siteTitle: false,

    search: {
      provider: "local",
    },

    nav: [
      { text: "Home", link: "/" },
      { text: "Notes", link: "/notes/" },
      { text: "Examples", link: "/examples/" },
    ],

    sidebar: sidebar_content,

    footer: {
      copyright:
        "Copyright © 2025–present <a href='https://abhigupta.io' target='_blank'>abhigupta.io</a>",
    },
  },
});
