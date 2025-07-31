"use client"

import { useState } from "react"
import { PhoneScanner } from "@/components/phone-scanner"
import { ScanHistory } from "@/components/scan-history"
import { MatrixBackground } from "@/components/matrix-background"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function Home() {
  const [activeTab, setActiveTab] = useState("scanner")

  return (
    <div className="min-h-screen bg-black text-green-400 relative overflow-hidden">
      <MatrixBackground />

      <div className="relative z-10">
        <header className="border-b border-green-400/20 bg-black/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-6">
            <h1 className="text-4xl font-bold text-center bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
              📱 PHONE INTELLIGENCE TOOLKIT
            </h1>
            <p className="text-center text-green-400/70 mt-2">Advanced OSINT Phone Number Analysis System</p>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-black/50 border border-green-400/20">
              <TabsTrigger
                value="scanner"
                className="data-[state=active]:bg-green-400/20 data-[state=active]:text-green-400"
              >
                🔍 Phone Scanner
              </TabsTrigger>
              <TabsTrigger
                value="history"
                className="data-[state=active]:bg-green-400/20 data-[state=active]:text-green-400"
              >
                📊 Scan History
              </TabsTrigger>
            </TabsList>

            <TabsContent value="scanner" className="mt-6">
              <PhoneScanner />
            </TabsContent>

            <TabsContent value="history" className="mt-6">
              <ScanHistory />
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
}
