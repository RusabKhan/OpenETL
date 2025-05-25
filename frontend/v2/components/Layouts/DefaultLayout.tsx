"use client";

import Head from "next/head";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { SidebarInset, SidebarProvider } from "../ui/sidebar";
import { AppSidebar } from "../app-sidebar";
import { SiteHeader } from "../site-header";
import { Toaster } from "../ui/sonner";
import { getTimezone } from "../utils/api";

export default function DefaultLayout({
  title,
  children,
}: Readonly<{
  title?: string;
  children: React.ReactNode;
}>) {
  const [token, setToken] = useState<string | null>(null);
  const [timezone, setTimezone] = useState<string>("UTC");
  const router = useRouter();

  const load_timezone = async () => {
    try {
      const response = await getTimezone();
      if (response) {
        setTimezone(response.data);
      }
    } catch (error) {
      console.error("Error loading timezone", error);
    }
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (!storedToken) {
      console.log("No token found, redirecting to login");
      router.push("/login");
    } else {
      load_timezone();
      setToken(storedToken);
    }
  }, []);

  return (
    <>
      <Head>
        <title>
          {title ? `${title} - OpenETL` : "Dashboard OpenETL"}
        </title>
        <meta name="description" content="Dashboard for OpenETL" />
      </Head>
      <div className="flex">
        <SidebarProvider
          style={
            {
              "--sidebar-width": "calc(var(--spacing) * 72)",
              "--header-height": "calc(var(--spacing) * 12)",
            } as React.CSSProperties
          }
        >
          <AppSidebar variant="inset" />
          <SidebarInset>
            <SiteHeader title={title} timezone={timezone} />
            {children}
          </SidebarInset>
        </SidebarProvider>
        <Toaster />
      </div>
    </>
  );
}
