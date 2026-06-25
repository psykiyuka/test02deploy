<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { Sparkles, Heart, MapPin, Phone, Mail, Instagram, Twitter, Facebook } from 'lucide-vue-next'
</script>

<template>
  <div class="layout-root">
    <AppHeader />

    <main class="layout-main">
      <RouterView />
    </main>

    <!-- ── Footer ── -->
    <footer class="site-footer">
      <!-- 分隔线 -->
      <div class="footer-deco-line" />

      <div class="footer-body">

        <!-- 订阅横幅 -->
        <div class="subscribe-band">
          <div class="subscribe-inner">
            <div class="subscribe-card">
              <div class="subscribe-text">
                <h3 class="subscribe-title">🌿 发现每一件有温度的好物</h3>
                <p class="subscribe-desc">订阅我们，第一时间获知新品上架与专属优惠</p>
              </div>
              <div class="subscribe-form">
                <input
                  type="email"
                  placeholder="您的邮箱地址"
                  class="subscribe-input"
                />
                <button class="subscribe-btn">订阅</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 主内容网格 -->
        <div class="footer-grid-wrap">
          <div class="footer-grid">

            <!-- 品牌列 -->
            <div class="footer-brand-col">
              <div class="footer-brand-logo">
                <div class="footer-brand-icon">
                  <Sparkles class="footer-brand-icon-svg" />
                </div>
                <div>
                  <span class="footer-brand-name">ELEGANCE</span>
                  <span class="footer-brand-sub">精致生活</span>
                </div>
              </div>
              <p class="footer-brand-desc">
                每一件商品，都经过我们精心甄选。<br />
                我们相信，美好的生活来自每一个用心的细节。
              </p>
              <div class="social-row">
                <a href="#" class="social-btn" aria-label="Instagram"><Instagram class="social-icon" /></a>
                <a href="#" class="social-btn" aria-label="Twitter"><Twitter class="social-icon" /></a>
                <a href="#" class="social-btn" aria-label="Facebook"><Facebook class="social-icon" /></a>
              </div>
            </div>

            <!-- 购物指南 -->
            <div>
              <h4 class="footer-heading">购物指南</h4>
              <ul class="footer-links">
                <li><router-link to="/products">全部商品</router-link></li>
                <li><router-link to="/products">热门推荐</router-link></li>
                <li><router-link to="/products">新品上架</router-link></li>
                <li><router-link to="/cart">我的购物车</router-link></li>
              </ul>
            </div>

            <!-- 用户服务 -->
            <div>
              <h4 class="footer-heading">用户服务</h4>
              <ul class="footer-links">
                <li><router-link to="/orders">我的订单</router-link></li>
                <li><router-link to="/profile">个人中心</router-link></li>
                <li><router-link to="/after-sales">售后服务</router-link></li>
                <li><a href="#" @click.prevent>常见问题</a></li>
              </ul>
            </div>

            <!-- 联系方式 -->
            <div>
              <h4 class="footer-heading">联系我们</h4>
              <ul class="contact-list">
                <li class="contact-item">
                  <Phone class="contact-icon" />
                  400-888-8888
                </li>
                <li class="contact-item">
                  <Mail class="contact-icon" />
                  support@elegance.shop
                </li>
                <li class="contact-item">
                  <MapPin class="contact-icon" />
                  工作时间：每日 9:00 – 21:00
                </li>
              </ul>
              <div class="badge-row">
                <span class="badge-warm">✓ 正品保证</span>
                <span class="badge-warm">✓ 7天退换</span>
                <span class="badge-warm">✓ 安全支付</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 版权栏 -->
        <div class="footer-copyright-bar">
          <div class="footer-copyright-inner">
            <p class="copyright-text">© 2026 ELEGANCE. All rights reserved.</p>
            <p class="copyright-love">
              Made with <Heart class="love-icon" /> by ELEGANCE Team
            </p>
          </div>
        </div>

      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ── 整体布局 ── */
.layout-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--warm-white, #fdf9f4);
}

.layout-main {
  flex: 1;
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  width: 100%;
  box-sizing: border-box;
}

/* ── Footer ── */
.site-footer {
  position: relative;
  overflow: hidden;
  margin-top: 5rem;
}

.footer-deco-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(212,169,106,0.4), transparent);
}

.footer-body {
  background: linear-gradient(135deg, #2A211A, #1E1710, #2A211A);
  color: rgba(255,255,255,0.65);
}

/* ── 订阅横幅 ── */
.subscribe-band {
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.subscribe-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}
.subscribe-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: rgba(255,255,255,0.04);
  border-radius: 20px;
  padding: 1.75rem 2rem;
  border: 1px solid rgba(255,255,255,0.06);
}
@media (min-width: 768px) {
  .subscribe-card { flex-direction: row; }
}

.subscribe-title {
  font-family: var(--font-display, 'Noto Serif SC', serif);
  color: #fff;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 6px;
}
.subscribe-desc {
  color: rgba(255,255,255,0.45);
  font-size: 0.875rem;
  margin: 0;
}
.subscribe-form {
  display: flex;
  gap: 8px;
  width: 100%;
}
@media (min-width: 768px) {
  .subscribe-form { width: auto; }
}

.subscribe-input {
  flex: 1;
  min-width: 0;
  padding: 9px 16px;
  border-radius: 12px;
  background: rgba(255,255,255,0.1);
  border: 1.5px solid rgba(255,255,255,0.15);
  color: #fff;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s;
}
.subscribe-input::placeholder { color: rgba(255,255,255,0.25); }
.subscribe-input:focus {
  border-color: rgba(196,144,64,0.6);
  background: rgba(255,255,255,0.15);
}
@media (min-width: 768px) {
  .subscribe-input { width: 240px; }
}

.subscribe-btn {
  flex-shrink: 0;
  padding: 9px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--gold-400, #c49040), var(--gold-500, #b5722a));
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(181,114,42,0.25);
  transition: all 0.2s;
}
.subscribe-btn:hover {
  background: linear-gradient(135deg, var(--gold-500, #b5722a), var(--gold-600, #8b5a1a));
}

/* ── 主内容网格 ── */
.footer-grid-wrap {
  max-width: 1280px;
  margin: 0 auto;
  padding: 3.5rem 1.5rem;
}
.footer-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}
@media (min-width: 640px) {
  .footer-grid { grid-template-columns: 1fr 1fr; }
}
@media (min-width: 1024px) {
  .footer-grid { grid-template-columns: 1.5fr 1fr 1fr 1.2fr; }
}

/* 品牌列 */
.footer-brand-col {}

.footer-brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.25rem;
}
.footer-brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--gold-300, #d4a96a), var(--gold-500, #b5722a));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 10px rgba(181,114,42,0.25);
  flex-shrink: 0;
}
.footer-brand-icon-svg {
  width: 18px;
  height: 18px;
  color: #fff;
}
.footer-brand-name {
  display: block;
  font-family: var(--font-display, 'Noto Serif SC', serif);
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.06em;
}
.footer-brand-sub {
  display: block;
  font-size: 9px;
  color: rgba(196,144,64,0.5);
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
.footer-brand-desc {
  font-size: 0.875rem;
  line-height: 1.7;
  color: rgba(255,255,255,0.38);
  margin-bottom: 1.5rem;
}

/* 社交按钮 */
.social-row {
  display: flex;
  gap: 8px;
}
.social-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.4);
  text-decoration: none;
  transition: all 0.2s;
}
.social-btn:hover {
  color: var(--gold-300, #d4a96a);
  background: rgba(255,255,255,0.12);
  border-color: rgba(181,114,42,0.35);
}
.social-icon { width: 15px; height: 15px; }

/* 页脚标题 */
.footer-heading {
  color: rgba(255,255,255,0.85);
  font-weight: 600;
  margin: 0 0 1rem;
  font-size: 0.875rem;
  letter-spacing: 0.025em;
  position: relative;
  padding-bottom: 0.625rem;
}
.footer-heading::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 2rem;
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--gold-400, #c49040), transparent);
}

/* 页脚链接 */
.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 0.875rem;
}
.footer-links a {
  color: rgba(255,255,255,0.4);
  text-decoration: none;
  transition: color 0.2s;
}
.footer-links a:hover { color: var(--gold-300, #d4a96a); }

/* 联系方式 */
.contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 0.875rem;
}
.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: rgba(255,255,255,0.4);
  transition: color 0.2s;
}
.contact-item:hover { color: rgba(255,255,255,0.65); }
.contact-icon {
  width: 15px;
  height: 15px;
  color: rgba(196,144,64,0.6);
  flex-shrink: 0;
  margin-top: 1px;
}

/* 服务徽章 */
.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 1.5rem;
}
.badge-warm {
  display: inline-block;
  font-size: 0.625rem;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.4);
  font-weight: 500;
  letter-spacing: 0.025em;
}

/* ── 版权栏 ── */
.footer-copyright-bar {
  border-top: 1px solid rgba(255,255,255,0.06);
}
.footer-copyright-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
@media (min-width: 640px) {
  .footer-copyright-inner { flex-direction: row; }
}
.copyright-text {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.22);
  margin: 0;
}
.copyright-love {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.18);
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
}
.love-icon {
  width: 12px;
  height: 12px;
  color: rgba(251,113,133,0.7);
}
</style>
