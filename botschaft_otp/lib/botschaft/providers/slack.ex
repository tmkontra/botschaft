defmodule Botschaft.Providers.Slack do
  use Botschaft.Provider, :slack

  def handle_call(
        {:message, %{destination: name, message: message}},
        _from,
        %{config: %{vars: shared_vars} = config} = state
      ) do
    case Botschaft.Config.ProviderConfig.get_destination_config(config, name) do
      %{"incoming_webhook_url" => url, "vars" => vars} ->
        vars = Map.merge(shared_vars, vars)
        message = Botschaft.Message.render(message, vars)

        case send_webhook(url, message) do
          :ok ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{
              provider: "slack",
              destination: name,
              success: true
            })

            {:reply, :ok, state}

          {:error, reason} ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{
              provider: "slack",
              destination: name,
              success: false
            })

            {:reply, {:error, reason}, state}
        end

      nil ->
        {:reply, {:error, "No slack destination #{name}"}, state}

      _ ->
        {:reply, {:error, "Slack destination #{name} has unsupported configuration"}, state}
    end
  end

  def send_webhook(url, message) do
    reply =
      Botschaft.Http.Client.post_json(url, %{
        "text" => message
      })

    if reply.status != 200 do
      {:error, "webhook rejected"}
    else
      :ok
    end
  end
end
