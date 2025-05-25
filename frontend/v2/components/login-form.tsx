"use client";

import React, { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "./utils/api";
import { LoginFormParam } from "./types/auth_params";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"form">) {
  const [data, setData] = React.useState<LoginFormParam>({
    username: "",
    password: "",
  });

  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      try {
        const res = await login(data);
        if (res.data) {
          localStorage.setItem("loggedin", "true");
          localStorage.setItem("token", res.data.access_token);
          router.push("/");
        }
      } catch (error: any) {
        if (error.response && error.response.status === 401) {
          toast.error(error.response.data.detail);
          return;
        }
        toast.error(error.message);
      }
    },
    [data, router]
  );

  useEffect(() => {
    document.title = "Login | OpenETL";
  }, []);

  return (
    <form
      className={cn("flex flex-col gap-6", className)}
      {...props}
      onSubmit={handleSubmit}
    >
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-2xl font-bold">Login to your account</h1>
        <p className="text-muted-foreground text-sm text-balance">
          Enter your username below to login to your account
        </p>
      </div>
      <div className="grid gap-6">
        <div className="grid gap-3">
          <Label htmlFor="username">Username</Label>
          <Input
            id="username"
            name="username"
            value={data.username}
            onChange={handleChange}
            type="text"
            placeholder="admin"
            required
          />
        </div>
        <div className="grid gap-3">
          <div className="flex items-center">
            <Label htmlFor="password">Password</Label>
          </div>
          <Input
            name="password"
            id="password"
            type="password"
            value={data.password}
            onChange={handleChange}
            required
          />
        </div>
        <Button type="submit" className="w-full">
          Login
        </Button>
      </div>
    </form>
  );
}
