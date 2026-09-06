import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

import PublicLayout from "./layouts/PublicLayout";
import MemberLayout from "./layouts/MemberLayout";
import AdminLayout from "./layouts/AdminLayout";
import SellerLayout from "./layouts/SellerLayout";

import Home from "./pages/Home";
import Products from "./pages/Products";
import ProductDetail from "./pages/ProductDetail";
import Franchise from "./pages/Franchise";
import Documents from "./pages/Documents";
import Pay from "./pages/Pay";
import Gallery from "./pages/Gallery";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Cart from "./pages/Cart";
import Join from "./pages/Join";
import Invoice from "./pages/Invoice";

import SellerAuth from "./pages/seller/SellerAuth";
import SellerDashboard from "./pages/seller/SellerDashboard";
import SellerEarnings from "./pages/seller/SellerEarnings";

import Dashboard from "./pages/member/Dashboard";
import Profile from "./pages/member/Profile";
import Team from "./pages/member/Team";
import LevelBonus from "./pages/member/LevelBonus";
import Orders from "./pages/member/Orders";
import Bonus from "./pages/member/Bonus";
import Payout from "./pages/member/Payout";
import Offers from "./pages/member/Offers";
import OfferProducts from "./pages/member/OfferProducts";
import IdCard from "./pages/member/IdCard";

import AdminLogin from "./pages/admin/AdminLogin";
import AdminOverview from "./pages/admin/Overview";
import AdminProducts from "./pages/admin/AdminProducts";
import AdminMembers from "./pages/admin/AdminMembers";
import AdminPayouts from "./pages/admin/AdminPayouts";
import AdminSettings from "./pages/admin/AdminSettings";

function RequireRole({ role, segment, children }) {
  const { auth } = useAuth();
  if (!auth) {
    const to = role === "admin" ? "/admin/login" : segment === "direct" ? "/seller/login" : "/";
    return <Navigate to={to} replace />;
  }
  if (auth.role !== role) return <Navigate to="/" replace />;
  // Keep the two member portals separate: send each segment to its own home.
  if (segment && auth.segment !== segment) {
    return <Navigate to={auth.segment === "direct" ? "/seller" : "/dashboard"} replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:slug" element={<ProductDetail />} />
        <Route path="/franchise" element={<Franchise />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/pay" element={<Pay />} />
        <Route path="/gallery" element={<Gallery />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/join" element={<Join />} />
      </Route>

      <Route
        path="/invoice/:orderId"
        element={
          <RequireRole role="member">
            <Invoice />
          </RequireRole>
        }
      />

      <Route path="/seller/login" element={<SellerAuth mode="login" />} />
      <Route path="/seller/signup" element={<SellerAuth mode="signup" />} />
      <Route
        path="/seller"
        element={
          <RequireRole role="member" segment="direct">
            <SellerLayout />
          </RequireRole>
        }
      >
        <Route index element={<SellerDashboard />} />
        <Route path="orders" element={<Orders />} />
        <Route path="earnings" element={<SellerEarnings />} />
        <Route path="payout" element={<Payout />} />
        <Route path="profile" element={<Profile />} />
        <Route path="id-card" element={<IdCard />} />
      </Route>

      <Route
        path="/dashboard"
        element={
          <RequireRole role="member" segment="mlm">
            <MemberLayout />
          </RequireRole>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="team" element={<Team />} />
        <Route path="level-bonus" element={<LevelBonus />} />
        <Route path="orders" element={<Orders />} />
        <Route path="bonus" element={<Bonus />} />
        <Route path="payout" element={<Payout />} />
        <Route path="offers" element={<Offers />} />
        <Route path="offer-products" element={<OfferProducts />} />
        <Route path="id-card" element={<IdCard />} />
      </Route>

      <Route path="/admin/login" element={<AdminLogin />} />
      <Route
        path="/admin"
        element={
          <RequireRole role="admin">
            <AdminLayout />
          </RequireRole>
        }
      >
        <Route index element={<AdminOverview />} />
        <Route path="products" element={<AdminProducts />} />
        <Route path="members" element={<AdminMembers />} />
        <Route path="payouts" element={<AdminPayouts />} />
        <Route path="settings" element={<AdminSettings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
