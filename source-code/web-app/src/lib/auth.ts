import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { connectToDatabase } from "@/lib/mongodb";
import User from "@/models/User";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        identifier: { label: "Username/Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.identifier || !credentials?.password) {
          throw new Error("Vui lòng điền đầy đủ tên đăng nhập/email và mật khẩu");
        }

        await connectToDatabase();

        const query = credentials.identifier.trim().toLowerCase();
        const user = await User.findOne({
          $or: [{ username: query }, { email: query }],
        });

        if (!user || !user.password) {
          throw new Error("Tài khoản hoặc mật khẩu không chính xác");
        }

        if (user.status === "Locked") {
          throw new Error("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên");
        }

        let isMatch = false;
        if (
          user.password.startsWith("$2a$") ||
          user.password.startsWith("$2b$") ||
          user.password.startsWith("$2y$")
        ) {
          isMatch = await bcrypt.compare(credentials.password, user.password);
        } else {
          isMatch = user.password === credentials.password;
        }

        if (!isMatch) {
          throw new Error("Tài khoản hoặc mật khẩu không chính xác");
        }

        // Chuẩn hóa role thành chữ in hoa theo tài liệu
        const normalizedRole = ((user.role as string) || "VIEWER").toUpperCase();

        return {
          id: user._id.toString(),
          name: user.fullname || user.username,
          email: user.email,
          username: user.username,
          role: normalizedRole,
          status: user.status || "Active",
        } as any;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = (user as any).id;
        token.username = (user as any).username;
        token.role = (user as any).role;
        token.fullname = user.name;
        token.status = (user as any).status;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id;
        (session.user as any).username = token.username;
        (session.user as any).role = token.role;
        (session.user as any).fullname = token.fullname;
        (session.user as any).status = token.status;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60,
  },
  secret: process.env.NEXTAUTH_SECRET || "tiktok_shop_bigdata_nhom17_secret_2026",
};
