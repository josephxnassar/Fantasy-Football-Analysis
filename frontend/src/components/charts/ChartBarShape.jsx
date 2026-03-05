import { Rectangle } from 'recharts';

export default function ChartBarShape(props) {
  const { index, payload, onBarClick, ...rectProps } = props;
  // Slight rank-based lightness shift makes adjacent bars easier to scan.
  const fill = `hsl(225, 73%, ${Math.max(40, 65 - index * 0.8)}%)`;

  return (
    <Rectangle
      {...rectProps}
      fill={fill}
      radius={[0, 4, 4, 0]}
      cursor="pointer"
      onClick={() => {
        // Recharts passes payload per bar; we bubble player name up to modal loader.
        if (payload?.name) onBarClick(payload.name);
      }}
    />
  );
}
