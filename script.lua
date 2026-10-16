-- Steal An Egg - CoreGui Teleport Hu
local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.2, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 340)
MainFrame.Active = true
MainFrame.Draggable = true

local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Teleport Areas Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

local function createButton(name, text, color, posY, callback)
    local btn = Instance.new("TextButton")
    btn.Name = name
    btn.Parent = MainFrame
    btn.BackgroundColor3 = color
    btn.Position = UDim2.new(0.1, 0, posY, 0)
    btn.Size = UDim2.new(0.8, 0, 0, 40)
    btn.Text = text
    btn.TextColor3 = Color3.fromRGB(255, 255, 255)
    btn.TextSize = 14
    btn.Font = Enum.Font.SourceSansBold
    btn.MouseButton1Click:Connect(callback)
    return btn
end

createButton("SpawnBtn", "منطقة البداية / الأمان 🛡️", Color3.fromRGB(50, 120, 200), 0.18, function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local spawn = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        if spawn then
            char.HumanoidRootPart.CFrame = spawn.CFrame + Vector3.new(0, 3, 0)
        else
            char.HumanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end)

local function teleportToArea(keyword)
    local char = LocalPlayer.Character
    if not char or not char:FindFirstChild("HumanoidRootPart") then return end
    local root = char.HumanoidRootPart
    
    local targetPart = nil
    for _, obj in ipairs(workspace:GetDescendants()) do
        if obj.Name:lower():find(keyword) then
            if obj:IsA("Model") and obj.PrimaryPart then
                targetPart = obj.PrimaryPart
                break
            elseif obj:IsA("BasePart") then
                targetPart = obj
                break
            end
        end
    end
    
    if targetPart then
        root.CFrame = targetPart.CFrame + Vector3.new(0, 3, 0)
    else
        root.CFrame = root.CFrame + (root.CFrame.LookVector * 100)
    end
end

createButton("Area1Btn", "الانتقال للمنطقة الأولى 📍", Color3.fromRGB(80, 80, 100), 0.35, function()
    teleportToArea("area1")
end)

createButton("Area2Btn", "الانتقال للمنطقة الثانية ⚡", Color3.fromRGB(150, 50, 200), 0.52, function()
    teleportToArea("area2")
end)

createButton("Area3Btn", "الانتقال للمنطقة المتقدمة 💎", Color3.fromRGB(220, 100, 30), 0.69, function()
    teleportToArea("area3")
end)

createButton("RespawnBtn", "إعادة توليد (Respawn) 🔄", Color3.fromRGB(200, 50, 50), 0.86, function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("Humanoid") then
        char.Humanoid.Health = 0
    end
end)
