import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export default function KnowledgeGraph({ concepts, highlightedConcept }) {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!concepts || concepts.length === 0) return;

    const width  = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Build nodes and links from concepts
    const nodes = concepts.map((c, i) => ({
      id:        i,
      name:      c.concept,
      frequency: c.frequency,
    }));

    // Link concepts that share similar words
    const links = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const wordsA = new Set(nodes[i].name.split(' '));
        const wordsB = new Set(nodes[j].name.split(' '));
        const shared = [...wordsA].filter(w => wordsB.has(w) && w.length > 3);
        if (shared.length > 0) {
          links.push({ source: i, target: j, shared });
        }
      }
    }

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link',   d3.forceLink(links).id(d => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50));

    // Draw links
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#2a2a3a')
      .attr('stroke-width', 1.5);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x; d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      );

    // Node circles
    node.append('circle')
      .attr('r', d => 14 + d.frequency * 6)
      .attr('fill', d =>
        d.name === highlightedConcept ? '#7c6af7' : '#1e1e2e'
      )
      .attr('stroke', d =>
        d.name === highlightedConcept ? '#a89cf7' : '#3a3a5a'
      )
      .attr('stroke-width', 1.5);

    // Node labels
    node.append('text')
      .text(d => d.name.length > 14 ? d.name.slice(0, 12) + '…' : d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('fill', '#c8c6df')
      .attr('font-size', '10px')
      .attr('pointer-events', 'none');

    // Tick update
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [concepts, highlightedConcept]);

  return (
    <div ref={svgRef} style={{ width: '100%', height: '100%' }} />
  );
}