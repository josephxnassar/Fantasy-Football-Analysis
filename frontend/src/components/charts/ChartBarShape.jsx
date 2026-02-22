import { Rectangle } from 'recharts';

export default function ChartBarShape(props) {
  const { index, payload, onBarClick, ...rectProps } = props;
  const fill = `hsl(225, 73%, ${Math.max(40, 65 - index * 0.8)}%)`;

  return (
    <Rectangle
      {...rectProps}
      fill={fill}
      radius={[0, 4, 4, 0]}
      cursor="pointer"
      onClick={() => {
        if (payload?.name) onBarClick(payload.name);
      }}
    />
  );
}
