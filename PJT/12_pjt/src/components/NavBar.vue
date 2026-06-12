<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="mt-nav">
    <div class="mt-nav__inner">
      <RouterLink to="/" class="mt-nav__brand">MyTube</RouterLink>
      <div class="mt-nav__menu">
        <RouterLink to="/" class="mt-nav__link">Home</RouterLink>
        <RouterLink to="/search" class="mt-nav__link">Search</RouterLink>
        <RouterLink to="/saved" class="mt-nav__link">Later</RouterLink>
        <RouterLink to="/channels" class="mt-nav__link">Channel</RouterLink>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.mt-nav {
  background: var(--mt-dark);
  color: #fff;
}
.mt-nav__inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 14px 20px;
}
.mt-nav__brand {
  font-weight: 800;
  font-size: 1.3rem;
  color: #fff;
  text-decoration: none;
}
.mt-nav__menu {
  display: flex;
  gap: 22px;
}
.mt-nav__link {
  color: #c4cad6;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.15s;
}
.mt-nav__link:hover {
  color: #fff;
}
.mt-nav__link.router-link-exact-active {
  color: #fff;
  font-weight: 700;
}
</style>
