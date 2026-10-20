"use client";

import React from "react";
import Link from "next/link";
import { Database, ArrowLeft, CheckCircle2 } from "lucide-react";
import Protection from "@/components/Protection";

export default function BackupRestorePage() {
  return (
    <Protection allowedRoles={["ADMIN"]}>
      <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6">
        <div className="bg-slate-950/60 border border-amber-500/30 rounded-3xl p-8 backdrop-blur-xl space-y-6">
          <div className="flex items-center gap-3">
            <span className="p-3 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/40">
              <Database className="w-7 h-7" />
            </span>
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Khu vực Quản trị Cấp Cao (ADMIN ONLY)
              </span>
              <h1 className="text-2xl font-black text-white mt-1">
                Sao Lưu & Phục Hồi Dữ Liệu (Backup / Restore)
              </h1>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-300 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong>Xác thực thành công:</strong> Bạn đang đăng nhập với quyền <strong>ADMIN</strong> tối cao. Hệ thống cho phép bạn truy cập vào trang quản trị sao lưu & phục hồi dữ liệu nhạy cảm của MongoDB Atlas.
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            📌 Chức năng gọi API xuất file JSON backup và khôi phục dữ liệu lên MongoDB Atlas sẽ do thành viên phụ trách tiếp tục phát triển theo khung Next.js của Leader.
          </p>

          <Link
            href="/orders"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition border border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Quay về trang Đơn hàng (/orders)</span>
          </Link>
        </div>
      </div>
    </Protection>
  );
}
