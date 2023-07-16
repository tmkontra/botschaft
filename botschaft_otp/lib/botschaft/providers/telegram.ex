defmodule Botschaft.Providers.Telegram do
  use GenServer

  @moduledoc false

  @r Req.new(base_url: "https://api.telegram.org")

  def start_link([get_config]) do
    config = get_config.(:telegram)
    GenServer.start_link(__MODULE__, %{config: config, get_config: get_config}, name: __MODULE__)
  end

  def get_config() do
    GenServer.call(__MODULE__, :get_config)
  end

  def reload_config() do
    GenServer.cast(__MODULE__, :reload)
  end

  def send(destination, message) when is_binary(message) do
    GenServer.call(__MODULE__, {:message, %{destination: destination, message: %{text: message}}})
  end

  def send(destination, %{message: _text, template: _template} = message) do
    GenServer.call(__MODULE__, {:message, %{destination: destination, message: message}})
  end

  def init(%{} = state) do
    {:ok, state}
  end

  def handle_call({:message, %{destination: name, message: message}}, _from, %{config: %{vars: shared_vars} = config} = state) do
    case get_destination(name, config) do
      %{"token" => token, "chat_id" => chat_id, "vars" => vars} ->
        vars = Map.merge(shared_vars, vars)
        message = Map.put(message, :vars, vars)
        case send_message(message, chat_id, token) do
          :ok ->
            {:reply, :ok, state}
          {:error, reason} ->
            {:reply, {:error, reason}, state}
        end
      nil ->
        {:reply, {:error, "No telegram destination #{name}"}, state}
    end
  end

  def handle_cast(:reload, %{get_config: get_config}) do
    {:noreply, %{config: get_config.(:telegram), get_config: get_config}}
  end

  defp get_destination(name, %{destinations: dests} = _config) do
    Map.get(dests, name)
  end

  defp send_message(%{text: text}, chat_id, bot_token) do
    send_message(text, chat_id, bot_token)
  end

  defp send_message(%{message: message, template: template, vars: vars}, chat_id, bot_token) do
    vars = Map.put(vars, "message", message)
    IO.puts "Rendering message with #{inspect vars}"
    contents = Solid.render!(template, vars) |> to_string
    send_message(contents, chat_id, bot_token)
  end

  defp send_message(text, chat_id, bot_token) do
    url = "/bot#{bot_token}/sendMessage"
    # https://core.telegram.org/bots/api#sendmessage
    resp = Req.get!(@r, url: url, params: [chat_id: chat_id, text: text])
    if resp.status != 200 do
      {:error, "Failed to send message: #{inspect resp}"}
    else
      :ok
    end
  end

end