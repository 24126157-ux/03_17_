import mongoose, { Schema, Document, Model } from "mongoose";

export type RoleType = "ADMIN" | "STAFF" | "VIEWER" | "Admin" | "Staff" | "Viewer" | "User" | "Analyst";

export interface IUser extends Document {
  username: string;
  email: string;
  password?: string;
  fullname?: string;
  role: RoleType;
  status: "Active" | "Locked";
  createdAt: Date;
  updatedAt: Date;
}

const UserSchema: Schema<IUser> = new Schema(
  {
    username: {
      type: String,
      required: [true, "Vui lòng nhập tên đăng nhập"],
      unique: true,
      trim: true,
      lowercase: true,
    },
    email: {
      type: String,
      required: [true, "Vui lòng nhập email"],
      unique: true,
      trim: true,
      lowercase: true,
    },
    password: {
      type: String,
      required: [true, "Vui lòng nhập mật khẩu"],
    },
    fullname: {
      type: String,
      default: "",
    },
    role: {
      type: String,
      enum: ["ADMIN", "STAFF", "VIEWER", "Admin", "Staff", "Viewer", "User", "Analyst"],
      default: "VIEWER",
    },
    status: {
      type: String,
      enum: ["Active", "Locked"],
      default: "Active",
    },
  },
  {
    timestamps: true,
    collection: "users",
  }
);

// Tránh lỗi OverwriteModelError khi Next.js hot-reload
const User: Model<IUser> =
  mongoose.models.User || mongoose.model<IUser>("User", UserSchema, "users");

export default User;
