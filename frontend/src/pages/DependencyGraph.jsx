import { useState, useEffect, useRef, useCallback } from 'react'
import {
  GitBranch,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  Maximize,
  Info,
  Shield,
  Move
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { graphAPI } from '../services/api'

export default function DependencyGraph() {
  const { currentAnalysis } = useAppStore()
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const [zoom, setZoom] = useState(1)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const canvasRef = useRef(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })

  useEffect(() => {
    if (currentAnalysis) {
      buildGraph()
    }
  }, [currentAnalysis])

  useEffect(() => {
    if (graphData && canvasRef.current) {
      drawGraph()
    }
  }, [graphData, zoom, offset, selectedNode, dimensions])

  const buildGraph = async () => {
    setLoading(true)
    try {
      const result = await graphAPI.getDependencyGraph(currentAnalysis)
      setGraphData(result)
    } catch (error) {
      console.error('Graph building failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const drawGraph = () => {
    const canvas = canvasRef.current
    if (!canvas || !graphData) return
    
    const ctx = canvas.getContext('2d')
    const width = dimensions.width
    const height = dimensions.height
    
    // Set canvas size
    canvas.width = width
    canvas.height = height
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height)
    
    if (!graphData.nodes || graphData.nodes.length === 0) {
      ctx.fillStyle = '#666'
      ctx.font = '14px monospace'
      ctx.textAlign = 'center'
      ctx.fillText('No dependencies detected', width / 2, height / 2)
      return
    }
    
    // Calculate node positions using force-directed layout
    const nodes = graphData.nodes.map(node => ({ ...node }))
    const centerX = width / 2 + offset.x
    const centerY = height / 2 + offset.y
    const radius = Math.min(width, height) * 0.35 * zoom
    
    // Position nodes in a circle
    nodes.forEach((node, index) => {
      const angle = (index / nodes.length) * Math.PI * 2
      node.x = centerX + Math.cos(angle) * radius
      node.y = centerY + Math.sin(angle) * radius
    })
    
    // Draw edges
    ctx.beginPath()
    graphData.edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source)
      const targetNode = nodes.find(n => n.id === edge.target)
      
      if (sourceNode && targetNode) {
        ctx.beginPath()
        ctx.moveTo(sourceNode.x, sourceNode.y)
        ctx.lineTo(targetNode.x, targetNode.y)
        ctx.strokeStyle = '#555'
        ctx.lineWidth = 1.5
        ctx.stroke()
        
        // Draw arrow
        const angle = Math.atan2(targetNode.y - sourceNode.y, targetNode.x - sourceNode.x)
        const arrowSize = 8
        const arrowX = targetNode.x - 15
        const arrowY = targetNode.y - 15
        ctx.beginPath()
        ctx.moveTo(targetNode.x, targetNode.y)
        ctx.lineTo(targetNode.x - arrowSize * Math.cos(angle - Math.PI / 6), 
                   targetNode.y - arrowSize * Math.sin(angle - Math.PI / 6))
        ctx.lineTo(targetNode.x - arrowSize * Math.cos(angle + Math.PI / 6), 
                   targetNode.y - arrowSize * Math.sin(angle + Math.PI / 6))
        ctx.fillStyle = '#666'
        ctx.fill()
      }
    })
    
    // Draw nodes
    nodes.forEach(node => {
      const isSelected = selectedNode === node.id
      const size = (node.size || 20) * zoom
      
      // Node color based on type
      let color, bgColor
      switch(node.type) {
        case 'api': color = '#3b82f6'; bgColor = 'rgba(59, 130, 246, 0.2)'; break
        case 'service': color = '#22c55e'; bgColor = 'rgba(34, 197, 94, 0.2)'; break
        case 'model': color = '#a855f7'; bgColor = 'rgba(168, 85, 247, 0.2)'; break
        case 'util': color = '#eab308'; bgColor = 'rgba(234, 179, 8, 0.2)'; break
        case 'test': color = '#ef4444'; bgColor = 'rgba(239, 68, 68, 0.2)'; break
        case 'component': color = '#06b6d4'; bgColor = 'rgba(6, 182, 212, 0.2)'; break
        case 'controller': color = '#f97316'; bgColor = 'rgba(249, 115, 22, 0.2)'; break
        case 'middleware': color = '#8b5cf6'; bgColor = 'rgba(139, 92, 246, 0.2)'; break
        default: color = '#6b7280'; bgColor = 'rgba(107, 114, 128, 0.2)'
      }
      
      // Draw shadow for selected node
      if (isSelected) {
        ctx.shadowBlur = 15
        ctx.shadowColor = color
      }
      
      // Draw node circle
      ctx.beginPath()
      ctx.arc(node.x, node.y, size / 2, 0, Math.PI * 2)
      ctx.fillStyle = bgColor
      ctx.fill()
      ctx.strokeStyle = color
      ctx.lineWidth = isSelected ? 3 : 2
      ctx.stroke()
      
      // Reset shadow
      ctx.shadowBlur = 0
      
      // Draw node label
      ctx.fillStyle = '#e5e5e5'
      ctx.font = `${Math.max(10, 12 * zoom)}px monospace`
      ctx.textAlign = 'center'
      ctx.fillText(node.name, node.x, node.y - size / 2 - 5)
      
      // Draw importance badge for high importance nodes
      if (node.importance > 8) {
        ctx.beginPath()
        ctx.arc(node.x + size / 2 - 5, node.y - size / 2 + 5, 8, 0, Math.PI * 2)
        ctx.fillStyle = '#f59e0b'
        ctx.fill()
        ctx.fillStyle = '#000'
        ctx.font = `${Math.max(8, 10 * zoom)}px monospace`
        ctx.fillText('★', node.x + size / 2 - 5, node.y - size / 2 + 8)
      }
      
      // Draw incoming/outgoing counts for selected node
      if (isSelected) {
        ctx.fillStyle = '#888'
        ctx.font = '10px monospace'
        ctx.fillText(`in:${node.incoming} out:${node.outgoing}`, node.x, node.y + size / 2 + 15)
      }
    })
  }

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current
    if (!canvas || !graphData) return
    
    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    
    const mouseX = (e.clientX - rect.left) * scaleX
    const mouseY = (e.clientY - rect.top) * scaleY
    
    // Find clicked node (simplified - would need to recalc positions)
    // For now, just toggle selection
    if (selectedNode) {
      setSelectedNode(null)
    } else if (graphData.nodes.length > 0) {
      setSelectedNode(graphData.nodes[0].id)
    }
  }

  const handleMouseDown = (e) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y })
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    setOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.1, 2))
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.1, 0.5))
  const handleReset = () => {
    setZoom(1)
    setOffset({ x: 0, y: 0 })
    setSelectedNode(null)
  }

  const getNodeTypeColor = (type) => {
    const colors = {
      api: 'border-blue-500 bg-blue-500/10 text-blue-400',
      service: 'border-green-500 bg-green-500/10 text-green-400',
      model: 'border-purple-500 bg-purple-500/10 text-purple-400',
      util: 'border-yellow-500 bg-yellow-500/10 text-yellow-400',
      test: 'border-red-500 bg-red-500/10 text-red-400',
      component: 'border-cyan-500 bg-cyan-500/10 text-cyan-400',
      controller: 'border-orange-500 bg-orange-500/10 text-orange-400',
      middleware: 'border-indigo-500 bg-indigo-500/10 text-indigo-400',
      module: 'border-gray-500 bg-gray-500/10 text-gray-400'
    }
    return colors[type] || colors.module
  }

  if (!currentAnalysis) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Repository Dependency Graph</h1>
        <div className="card text-center py-12">
          <GitBranch className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Repository Analyzed</h3>
          <p className="text-dark-300">First analyze a repository to see dependency graph</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Repository Dependency Graph</h1>
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-dark-300">Building dependency graph...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Repository Dependency Graph</h1>
        <div className="flex space-x-2">
          <button onClick={handleZoomIn} className="btn-secondary p-2" title="Zoom In">
            <ZoomIn className="w-4 h-4" />
          </button>
          <button onClick={handleZoomOut} className="btn-secondary p-2" title="Zoom Out">
            <ZoomOut className="w-4 h-4" />
          </button>
          <button onClick={handleReset} className="btn-secondary p-2" title="Reset View">
            <Maximize className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Graph Canvas */}
        <div className="lg:col-span-3">
          <div className="card p-0 overflow-hidden">
            <div 
              className="relative"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
            >
              <canvas
                ref={canvasRef}
                width={800}
                height={600}
                className="w-full h-[500px] bg-dark-900"
                onClick={handleCanvasClick}
              />
              <div className="absolute bottom-2 right-2 text-xs text-dark-400 bg-dark-800 px-2 py-1 rounded">
                Drag to pan • Click nodes for details
              </div>
            </div>
          </div>
        </div>

        {/* Info Panel */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Graph Info</h3>
            {graphData && (
              <span className="text-xs text-dark-400">
                {graphData.nodes.length} nodes, {graphData.edges.length} edges
              </span>
            )}
          </div>

          {graphData && (
            <div className="space-y-4 max-h-[500px] overflow-y-auto">
              {/* Statistics */}
              <div className="grid grid-cols-2 gap-2">
                <div className="text-center p-2 bg-dark-800 rounded">
                  <p className="text-xl font-bold text-blue-400">{graphData.statistics.total_modules}</p>
                  <p className="text-xs text-dark-400">Modules</p>
                </div>
                <div className="text-center p-2 bg-dark-800 rounded">
                  <p className="text-xl font-bold text-green-400">{graphData.statistics.total_dependencies}</p>
                  <p className="text-xs text-dark-400">Dependencies</p>
                </div>
                <div className="text-center p-2 bg-dark-800 rounded">
                  <p className="text-xl font-bold text-yellow-400">{graphData.statistics.circular_count}</p>
                  <p className="text-xs text-dark-400">Circular</p>
                </div>
                <div className="text-center p-2 bg-dark-800 rounded">
                  <p className="text-xl font-bold text-purple-400">{graphData.statistics.avg_dependencies}</p>
                  <p className="text-xs text-dark-400">Avg/Module</p>
                </div>
              </div>

              {/* Metrics */}
              <div className="border-t border-dark-700 pt-3">
                <h4 className="text-sm font-medium mb-2">📊 Metrics</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-dark-300">Avg Incoming:</span>
                    <span>{graphData.metrics.avg_incoming}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dark-300">Avg Outgoing:</span>
                    <span>{graphData.metrics.avg_outgoing}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dark-300">Max Incoming:</span>
                    <span>{graphData.metrics.max_incoming}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dark-300">Density:</span>
                    <span>{graphData.metrics.density}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-dark-300">Most Connected:</span>
                    <span className="text-blue-400 truncate max-w-[150px]">
                      {graphData.metrics.most_connected || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Circular Dependencies Warning */}
              {graphData.circular_dependencies && graphData.circular_dependencies.length > 0 && (
                <div className="border-t border-dark-700 pt-3">
                  <div className="flex items-center text-yellow-400 mb-2">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    <h4 className="text-sm font-medium">Circular Dependencies</h4>
                  </div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {graphData.circular_dependencies.slice(0, 3).map((circ, idx) => (
                      <div key={idx} className="text-xs bg-dark-800 p-2 rounded">
                        <span className="text-yellow-400">Cycle:</span>
                        <span className="text-dark-300 ml-1">
                          {circ.cycle.slice(0, 4).join(' → ')}
                          {circ.length > 3 ? '...' : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Selected Node Info */}
              {selectedNode && graphData.nodes.find(n => n.id === selectedNode) && (
                <div className="border-t border-dark-700 pt-3">
                  <h4 className="text-sm font-medium mb-2">🔍 Selected Node</h4>
                  {(() => {
                    const node = graphData.nodes.find(n => n.id === selectedNode)
                    return (
                      <div className={`rounded-lg p-3 ${getNodeTypeColor(node?.type)}`}>
                        <p className="font-mono font-medium">{node?.name}</p>
                        <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                          <div>
                            <span className="text-dark-400">Type:</span>
                            <span className="ml-1 capitalize">{node?.type}</span>
                          </div>
                          <div>
                            <span className="text-dark-400">Importance:</span>
                            <span className="ml-1">{node?.importance}</span>
                          </div>
                          <div>
                            <span className="text-dark-400">Incoming:</span>
                            <span className="ml-1 text-green-400">{node?.incoming}</span>
                          </div>
                          <div>
                            <span className="text-dark-400">Outgoing:</span>
                            <span className="ml-1 text-red-400">{node?.outgoing}</span>
                          </div>
                        </div>
                      </div>
                    )
                  })()}
                </div>
              )}

              {/* Legend */}
              <div className="border-t border-dark-700 pt-3">
                <h4 className="text-sm font-medium mb-2">🎨 Legend</h4>
                <div className="grid grid-cols-2 gap-1 text-xs">
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>API</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>Service</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>Model</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>Util</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>Test</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-cyan-500 mr-2"></div>Component</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-orange-500 mr-2"></div>Controller</div>
                  <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-indigo-500 mr-2"></div>Middleware</div>
                </div>
                <div className="mt-2 pt-2 border-t border-dark-700 text-xs text-dark-400">
                  <div className="flex items-center"><span className="text-yellow-500 mr-2">★</span> High importance node</div>
                  <div className="flex items-center mt-1"><span className="text-gray-400 mr-2">→</span> Dependency direction</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Info Banner */}
      <div className="mt-6 card bg-blue-500/10 border border-blue-500/20">
        <div className="flex items-start">
          <Info className="w-5 h-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium mb-1">About the Dependency Graph</h3>
            <ul className="text-xs text-dark-300 space-y-1">
              <li>• <strong>Nodes</strong> represent modules/files. Size indicates importance</li>
              <li>• <strong>Edges</strong> show dependencies (arrows point from importer to imported)</li>
              <li>• <strong>Yellow stars</strong> highlight high-importance modules</li>
              <li>• <strong>Circular dependencies</strong> (red warnings) may cause maintenance issues</li>
              <li>• <strong>Drag canvas</strong> to pan • <strong>Scroll</strong> to zoom • <strong>Click nodes</strong> for details</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}