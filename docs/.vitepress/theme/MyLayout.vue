<!--.vitepress/theme/MyLayout.vue-->
<script setup>
import DefaultTheme from 'vitepress/theme'

const { Layout } = DefaultTheme
</script>

<template>
  <Layout>
    <template #home-hero-image>
      <img src="./vitepress-logo-large.svg" alt="VitePress Logo" class="hero-video"
        style="z-index: 10; position: relative;" />
    </template>

  </Layout>
</template>

<style scoped>


.hero-video {
  /* margin-top: calc((var(--vp-nav-height) + var(--vp-layout-top-height, 0px)) * -1); */
  /* padding: calc(var(--vp-nav-height) + var(--vp-layout-top-height, 0px) + 48px) 24px 48px; */
  /* height: 300px; */

}

@media (min-width: 640px) {
  .hero-video {
    height: 400px;
  }

}

@media (min-width: 960px) {
  .hero-video {
    margin-left: 2rem;
    width: 100%;
    height: 450px;
  }
}
</style>