"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Trash2, Search, Eye } from "lucide-react"
import { ScanResults } from "./scan-results"

interface SavedScan {
  phone_number: string
  scan_date: string
  status: string
  results: any
}

export function ScanHistory() {
  const [savedScans, setSavedScans] = useState<SavedScan[]>([])
  const [selectedScan, setSelectedScan] = useState<SavedScan | null>(null)
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    const scans = JSON.parse(localStorage.getItem("phoneScans") || "[]")
    setSavedScans(scans)
  }, [])

  const filteredScans = savedScans.filter(
    (scan) =>
      scan.phone_number.includes(searchTerm) || new Date(scan.scan_date).toLocaleDateString().includes(searchTerm),
  )

  const deleteScan = (phoneNumber: string, scanDate: string) => {
    const updatedScans = savedScans.filter(
      (scan) => !(scan.phone_number === phoneNumber && scan.scan_date === scanDate),
    )
    setSavedScans(updatedScans)
    localStorage.setItem("phoneScans", JSON.stringify(updatedScans))

    if (selectedScan?.phone_number === phoneNumber && selectedScan?.scan_date === scanDate) {
      setSelectedScan(null)
    }
  }

  const clearAllScans = () => {
    setSavedScans([])
    setSelectedScan(null)
    localStorage.removeItem("phoneScans")
  }

  if (selectedScan) {
    return (
      <div className="space-y-4">
        <Button
          onClick={() => setSelectedScan(null)}
          variant="outline"
          className="bg-green-400/20 hover:bg-green-400/30 text-green-400 border-green-400/20"
        >
          ← Back to History
        </Button>
        <ScanResults results={selectedScan.results} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card className="bg-black/50 border-green-400/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-green-400">
            <span>📊 Scan History</span>
            {savedScans.length > 0 && (
              <Button
                onClick={clearAllScans}
                variant="outline"
                size="sm"
                className="bg-red-400/20 hover:bg-red-400/30 text-red-400 border-red-400/20"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                Clear All
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-green-400/50" />
              <Input
                placeholder="Search by phone number or date..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-black/50 border-green-400/20 text-green-400 placeholder:text-green-400/50"
              />
            </div>
          </div>

          {filteredScans.length === 0 ? (
            <div className="text-center py-12 text-green-400/50">
              {savedScans.length === 0 ? (
                <>
                  <div className="text-6xl mb-4">📱</div>
                  <div className="text-lg mb-2">No scans yet</div>
                  <div className="text-sm">Start your first phone number scan to see results here</div>
                </>
              ) : (
                <>
                  <div className="text-6xl mb-4">🔍</div>
                  <div className="text-lg mb-2">No matching scans</div>
                  <div className="text-sm">Try adjusting your search terms</div>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredScans.map((scan, index) => (
                <div
                  key={`${scan.phone_number}-${scan.scan_date}`}
                  className="flex items-center justify-between p-4 rounded-lg bg-black/30 border border-green-400/10 hover:border-green-400/20 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-green-400 font-medium">{scan.phone_number}</span>
                      <Badge
                        variant="outline"
                        className={
                          scan.status === "completed"
                            ? "bg-green-400/20 text-green-400 border-green-400/20"
                            : "bg-red-400/20 text-red-400 border-red-400/20"
                        }
                      >
                        {scan.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-green-400/70 mt-1">
                      Scanned: {new Date(scan.scan_date).toLocaleString()}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      onClick={() => setSelectedScan(scan)}
                      size="sm"
                      variant="outline"
                      className="bg-green-400/20 hover:bg-green-400/30 text-green-400 border-green-400/20"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      onClick={() => deleteScan(scan.phone_number, scan.scan_date)}
                      size="sm"
                      variant="outline"
                      className="bg-red-400/20 hover:bg-red-400/30 text-red-400 border-red-400/20"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
