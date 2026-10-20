"use client";

import React, { useState, useEffect } from "react";
import { signIn, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  Lock,
  User as UserIcon,
  Eye,
  EyeOff,
  LogIn,
  Crown,
  Briefcase,
  Eye as ViewerIcon,
  AlertCircle,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { data: session, status } = useSession();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Nếu đã đăng nhập thì điều hướng về trang chủ
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/orders");
    }
  }, [status, router]);

  // Tự động gọi seed tài khoản mẫu một lần
  useEffect(() => {
    fetch("/api/auth/seed").catch(() => {});
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setLoading(true);

    try {
      const res = await signIn("credentials", {
        identifier,
        password,
        redirect: false,
      });

      if (res?.error) {
        setErrorMessage(res.error);
        setLoading(false);
      } else {
        setSuccessMessage("Đăng nhập thành công! Đang chuyển hướng...");
        setTimeout(() => {
          router.push("/orders");
          router.refresh();
        }, 800);
      }
    } catch (err: any) {
      setErrorMessage("Đã xảy ra lỗi trong quá trình đăng nhập. Vui lòng thử lại!");
      setLoading(false);
    }
  };

  const handleFillDemo = (demoUser: string, demoPass: string) => {
    setIdentifier(demoUser);
    setPassword(demoPass);
    setErrorMessage("");
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-gradient-to-br from-[#0b0f19] via-[#111827] to-[#1e1b4b]">
      {/* Background Glow Decorations */}
      <div className="fixed top-1/4 left-1/4 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/15 rounded-full blur-3xl pointer-events-none" />

      <div className="relative w-full max-w-md bg-white/95 dark:bg-zinc-900/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-zinc-200/80 dark:border-zinc-800/80 p-8 sm:p-10 z-10">
        {/* Header & Logo */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 mb-4">
            <svg
              className="w-9 h-9 fill-current"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1.04-.1z" />
            </svg>
          </div>
          <h1 className="text-2xl font-black tracking-tight text-zinc-900 dark:text-white uppercase">
            TikTok Shop Portal
          </h1>
          <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 mt-1 uppercase tracking-wider">
            Cổng Phân Tích Dữ Liệu Lớn & Quản Trị Hệ Thống • Nhóm 17
          </p>
          <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-[11px] font-medium border border-indigo-200/60 dark:border-indigo-800/60">
            <Sparkles className="w-3.5 h-3.5" /> Nhiệm vụ 1B: Xác thực & Phân quyền RBAC
          </div>
        </div>

        {/* Alerts */}
        {errorMessage && (
          <div className="mb-6 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900/60 flex items-start gap-2.5 text-red-700 dark:text-red-300 text-xs font-medium animate-shake">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-900/60 flex items-start gap-2.5 text-emerald-700 dark:text-emerald-300 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-500" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Form Đăng Nhập */}
        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-2 uppercase tracking-wider">
              Tên đăng nhập hoặc Email
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-400">
                <UserIcon className="w-4 h-4" />
              </div>
              <input
                type="text"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="Nhập username hoặc email..."
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-800/80 text-zinc-900 dark:text-white placeholder:text-zinc-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-2 uppercase tracking-wider">
              Mật khẩu
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-400">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu..."
                className="w-full pl-10 pr-11 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-800/80 text-zinc-900 dark:text-white placeholder:text-zinc-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-4 bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-bold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                <span>Đăng Nhập Hệ Thống</span>
              </>
            )}
          </button>
        </form>

        {/* Demo Accounts Quick-Fill Box */}
        <div className="mt-8 pt-6 border-t border-zinc-100 dark:border-zinc-800/80">
          <p className="text-[11px] font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-3 flex items-center justify-between">
            <span>Tài khoản mẫu kiểm thử 3 vai trò (RBAC):</span>
          </p>

          <div className="grid grid-cols-1 gap-2.5">
            {/* ADMIN */}
            <button
              type="button"
              onClick={() => handleFillDemo("admin", "admin123")}
              className="flex items-center justify-between p-2.5 rounded-xl border border-purple-200 dark:border-purple-900/50 bg-purple-50/60 dark:bg-purple-950/20 hover:bg-purple-100/70 dark:hover:bg-purple-900/40 transition group text-left"
            >
              <div className="flex items-center gap-2.5">
                <span className="w-7 h-7 rounded-lg bg-purple-600 text-white flex items-center justify-center shadow-sm">
                  <Crown className="w-4 h-4" />
                </span>
                <div>
                  <div className="text-xs font-bold text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
                    ADMIN
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-200 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 font-semibold">
                      Toàn quyền
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-500 dark:text-zinc-400 font-mono">
                    admin / admin123
                  </div>
                </div>
              </div>
              <span className="text-[10px] text-purple-600 font-medium opacity-0 group-hover:opacity-100 transition">
                Điền nhanh →
              </span>
            </button>

            {/* STAFF */}
            <button
              type="button"
              onClick={() => handleFillDemo("staff", "staff123")}
              className="flex items-center justify-between p-2.5 rounded-xl border border-blue-200 dark:border-blue-900/50 bg-blue-50/60 dark:bg-blue-950/20 hover:bg-blue-100/70 dark:hover:bg-blue-900/40 transition group text-left"
            >
              <div className="flex items-center gap-2.5">
                <span className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-sm">
                  <Briefcase className="w-4 h-4" />
                </span>
                <div>
                  <div className="text-xs font-bold text-blue-900 dark:text-blue-300 flex items-center gap-1.5">
                    STAFF
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-blue-200 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 font-semibold">
                      Đơn hàng & Báo cáo
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-500 dark:text-zinc-400 font-mono">
                    staff / staff123
                  </div>
                </div>
              </div>
              <span className="text-[10px] text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition">
                Điền nhanh →
              </span>
            </button>

            {/* VIEWER */}
            <button
              type="button"
              onClick={() => handleFillDemo("viewer", "user123")}
              className="flex items-center justify-between p-2.5 rounded-xl border border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/60 dark:bg-emerald-950/20 hover:bg-emerald-100/70 dark:hover:bg-emerald-900/40 transition group text-left"
            >
              <div className="flex items-center gap-2.5">
                <span className="w-7 h-7 rounded-lg bg-emerald-600 text-white flex items-center justify-center shadow-sm">
                  <ViewerIcon className="w-4 h-4" />
                </span>
                <div>
                  <div className="text-xs font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                    VIEWER
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-200 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 font-semibold">
                      Chỉ xem & lọc
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-500 dark:text-zinc-400 font-mono">
                    viewer / user123
                  </div>
                </div>
              </div>
              <span className="text-[10px] text-emerald-600 font-medium opacity-0 group-hover:opacity-100 transition">
                Điền nhanh →
              </span>
            </button>
          </div>

          <p className="mt-3 text-[10px] text-zinc-400 text-center">
            * Bấm trực tiếp vào từng ô trên để tự động điền nhanh tài khoản!
          </p>
        </div>
      </div>
    </div>
  );
}
