defmodule Botschaft.Message do
  defstruct [:text, :template]

  def text(text) do
    %__MODULE__{text: text}
  end

  def template(template, text) do
    %__MODULE__{text: text, template: template}
  end

  def render(%__MODULE__{text: text, template: template}, vars) do
    render(text, template, vars)
  end

  defp render(text, nil = _template, _vars) do
    text
  end

  defp render(text, template, vars) do
    vars = Map.put(vars, "message", text)
    IO.puts "Rendering message with #{inspect vars}"
    Solid.render!(template, vars) |> to_string
  end
end
