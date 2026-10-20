import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { connectToDatabase } from "@/lib/mongodb";
import User, { RoleType } from "@/models/User";

export async function GET() {
  try {
    await connectToDatabase();

    const sampleUsers: Array<{
      username: string;
      email: string;
      password: string;
      fullname: string;
      role: RoleType;
      status: "Active" | "Locked";
    }> = [
      {
        username: "admin",
        email: "admin@tiktokshop.portal",
        password: await bcrypt.hash("admin123", 10),
        fullname: "Quản Trị Viên (Admin)",
        role: "ADMIN",
        status: "Active",
      },
      {
        username: "staff",
        email: "staff@tiktokshop.portal",
        password: await bcrypt.hash("staff123", 10),
        fullname: "Nhân Viên Vận Hành (Staff)",
        role: "STAFF",
        status: "Active",
      },
      {
        username: "viewer",
        email: "viewer@tiktokshop.portal",
        password: await bcrypt.hash("user123", 10),
        fullname: "Khách Xem Báo Cáo (Viewer)",
        role: "VIEWER",
        status: "Active",
      },
      {
        username: "khachhang",
        email: "khachhang@tiktokshop.portal",
        password: await bcrypt.hash("user123", 10),
        fullname: "Khách Hàng Trải Nghiệm (User)",
        role: "VIEWER",
        status: "Active",
      },
    ];

    let createdCount = 0;
    for (const u of sampleUsers) {
      const existing = await User.findOne({ username: u.username });
      if (!existing) {
        await User.create(u);
        createdCount++;
      } else {
        existing.role = u.role;
        await existing.save();
      }
    }

    return NextResponse.json({
      success: true,
      message: `Khởi tạo người dùng mẫu thành công. Đã thêm mới ${createdCount} tài khoản.`,
    });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
