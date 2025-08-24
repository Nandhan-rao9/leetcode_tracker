export default function ProblemRow({ item }) {
  return (
    <tr>
      <td><a href={item.url} target="_blank" rel="noreferrer">{item.title}</a></td>
      <td>{item.difficulty || "-"}</td>
      <td>{(item.lcTags || []).join(", ")}</td>
      <td style={{textAlign:"right"}}>{item.numOccur ?? "-"}</td>
      <td>{item.lastSolvedAt ? new Date(item.lastSolvedAt).toLocaleDateString() : "-"}</td>
    </tr>
  );
}
