defmodule Botschaft.Http.Client do
  alias Req

  def get(url, params \\ []) do
    Req.get!(url, params: params)
  end

  def post_json(url, body, params \\ []) when is_map(body) do
    Req.post!(url, json: body, params: params)
  end

  def post(url, args \\ []) do
    Req.post!(url, args)
  end
end
