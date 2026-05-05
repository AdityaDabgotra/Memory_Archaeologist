import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export default function KnowledgeGraph({ concepts, highlightedConcept }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!concepts?.length || !ref.current) return;

    const W = ref.current.clientWidth;
    const H = ref.current.clientHeight;
    const PADDING = 60; // keep nodes this far from edges

    d3.select(ref.current).selectAll('*').remove();

    const svg = d3.select(ref.current)
      .append('svg')
      .attr('width', W)
      .attr('height', H);

    const nodes = concepts.map((c, i) => ({
      id:   i,
      name: c.concept,
      freq: c.frequency,
      // start nodes near center instead of random positions
      x: W / 2 + (Math.random() - 0.5) * 100,
      y: H / 2 + (Math.random() - 0.5) * 100,
    }));

    const links = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const wa = new Set(nodes[i].name.split(' '));
        const wb = new Set(nodes[j].name.split(' '));
        const shared = [...wa].filter(w => wb.has(w) && w.length > 3);
        if (shared.length) links.push({ source: i, target: j });
      }
    }

    const sim = d3.forceSimulation(nodes)
      .force('link',      d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge',    d3.forceManyBody().strength(-180))
      .force('center',    d3.forceCenter(W / 2, H / 2).strength(0.8))
      .force('collision', d3.forceCollide().radius(50))
      // pull nodes back toward center — prevents scatter
      .force('x', d3.forceX(W / 2).strength(0.08))
      .force('y', d3.forceY(H / 2).strength(0.08));

    svg.append('g').selectAll('line')
      .data(links).join('line')
      .attr('stroke', '#E4E2DA')
      .attr('stroke-width', 1);

    const node = svg.append('g').selectAll('g')
      .data(nodes).join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (e, d) => {
          if (!e.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (e, d) => {
          // clamp dragging within bounds too
          d.fx = Math.max(PADDING, Math.min(W - PADDING, e.x));
          d.fy = Math.max(PADDING, Math.min(H - PADDING, e.y));
        })
        .on('end', (e, d) => {
          if (!e.active) sim.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      );

    const isHL = d => d.name === highlightedConcept;

    node.append('circle')
      .attr('r', d => 16 + d.freq * 4)
      .attr('fill',         d => isHL(d) ? '#2D5016' : '#FFFFFF')
      .attr('stroke',       d => isHL(d) ? '#2D5016' : '#D8D6CE')
      .attr('stroke-width', 1.5);

    node.append('text')
      .text(d => d.name.length > 16 ? d.name.slice(0, 14) + '...' : d.name)
      .attr('text-anchor',    'middle')
      .attr('dy',             '0.35em')
      .attr('fill',           d => isHL(d) ? '#FFFFFF' : '#4A4845')
      .attr('font-size',      '10px')
      .attr('font-family',    'DM Sans, sans-serif')
      .attr('pointer-events', 'none');

    sim.on('tick', () => {
      // clamp every node within bounds on each tick
      nodes.forEach(d => {
        d.x = Math.max(PADDING, Math.min(W - PADDING, d.x));
        d.y = Math.max(PADDING, Math.min(H - PADDING, d.y));
      });

      svg.selectAll('line')
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => sim.stop();
  }, [concepts, highlightedConcept]);

  return <div ref={ref} style={{ width: '100%', height: '100%' }} />;
}