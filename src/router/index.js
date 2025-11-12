import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import About from '../components/About.vue'
import Term from '../components/Term.vue'
import Koleksi from '../components/Koleksi.vue'
import Contact from '../components/Contact.vue'
import Product from '../components/Product.vue'
import Member from '../components/Member.vue'
import Koko from '../components/Koko.vue'
import Login from '../components/Login.vue'
import SignUp from '../components/SignUp.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/term',
    name: 'Term & Conditions',
    component: Term
  },
  {
    path: '/koleksi',
    name: 'Koleksi',
    component: Koleksi
  },
  {
    path: '/contact',
    name: 'Contact Us',
    component: Contact
  },
  {
    path: '/product',
    name: 'Product',
    component: Product
  },
  {
    path: '/member',
    name: 'Member',
    component: Member
  },
  {
    path: '/koko',
    name: 'Koko',
    component: Koko
  },
  {
  path: '/productdetail/:id',
  name: 'ProductDetail',
  component: () => import('../components/ProductDetail.vue')
  },
  {
  path: '/login',
  name: 'Login',
  component: Login
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp
  },
  {
  path: '/checkout',
  name: 'Checkout',
  component: () => import('../components/Checkout.vue')
  },
  {
  path: '/order-detail',
  name: 'OrderDetail',
  component: () => import('../components/OrderDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return { top: 0, behavior: 'smooth' }
  }
})

export default router