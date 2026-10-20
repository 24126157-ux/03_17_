"use client";

import React from "react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { Package, ShieldAlert, ArrowRight, Database } from "lucide-react";
import Protection from "@/components/Protection";

export default function OrdersPage() {
  const { data: session } = useSession();
  const role = ((session?.user as any)?.role || "VIEWER").toUpperCase();

  return (
    <Protection allowedRoles={["ADMIN", "STAFF", "VIEWER"]}>
      <div className="max-w-5xl mx-auto py-10 px-4 sm:px-6 space-y-8">
        {/* Header Trang */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-2">
            <span className="p-2.5 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <Package className="w-6 h-6" />
            </span>
            <div>
              <h1 className="text-2xl font-black text-white">
                Quản Lý Đơn Hàng TikTok Shop
              </h1>
              <p className="text-xs text-indigo-400 font-mono">
                Đã xác thực thành công
              </p>
            </div>
          </div>
          <p className="text-sm text-slate-300 mt-3 leading-relaxed">
            Bạn đã đăng nhập thành công với vai trò:{" "}
            <strong className="text-indigo-400 uppercase font-bold">{role}</strong>. Trang này sẵn sàng đón nhận giao diện bảng dữ liệu đơn hàng (DataTable), bộ lọc tìm kiếm và các nút CRUD do thành viên phụ trách tiếp tục phát triển.
          </p>
        </div>

        {/* Khung Test Role Guard */}
        <div className="bg-slate-950/40 border border-slate-800/80 rounded-2xl p-6">
          <h2 className="text-sm font-bold text-white flex items-center gap-2 mb-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            Khu vực kiểm thử Role Guard (RBAC):
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Nếu tài khoản <strong>không phải ADMIN</strong> (ví dụ: đang đăng nhập là <strong>{role}</strong>) mà bấm vào trang <code>/backup-restore</code> thì hệ thống sẽ tự động chặn quyền truy cập.
          </p>

          <Link
            href="/backup-restore"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 text-xs font-semibold transition"
          >
            <Database className="w-4 h-4" />
            <span>Thử truy cập trang /backup-restore (Để kiểm tra chặn quyền)</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
      </div>
    </Protection>
  );
}
